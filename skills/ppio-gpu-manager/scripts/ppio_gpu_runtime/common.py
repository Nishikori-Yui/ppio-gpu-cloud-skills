from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_GPU_API_BASE = "https://api.ppio.com/gpu-instance/openapi/v1"
DEFAULT_CORE_API_BASE = "https://api.ppio.com/openapi/v1"
DEFAULT_USER_API_BASE = "https://api.ppio.com/v3"
DEFAULT_TIMEOUT = 30.0
REDACTED = "***REDACTED***"
SECRET_FIELD_NAMES = {
    "accesskey",
    "accesstoken",
    "api_key",
    "apikey",
    "authorization",
    "password",
    "privatekey",
    "secret",
    "sshpassword",
    "token",
}


class CliError(Exception):
    pass


def parse_dotenv_line(raw_line: str) -> tuple[str, str] | None:
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return None
    if line.startswith("export "):
        line = line[len("export ") :].strip()
    key, separator, value = line.partition("=")
    if not separator:
        return None
    key = key.strip()
    value = value.strip()
    if not key:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return key, value


def load_dotenv_file(path: Path) -> bool:
    loaded = False
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            parsed = parse_dotenv_line(line)
            if parsed is None:
                continue
            key, value = parsed
            os.environ.setdefault(key, value)
            loaded = True
    return loaded


def iter_parent_env_files(start: Path) -> list[Path]:
    candidates: list[Path] = []
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for directory in [current, *current.parents]:
        candidates.append(directory / ".env")
    return candidates


def bootstrap_environment(script_path: str) -> Path | None:
    roots = [Path(script_path).resolve().parent, Path.cwd()]
    seen: set[Path] = set()
    for root in roots:
        for candidate in iter_parent_env_files(root):
            resolved = candidate.resolve(strict=False)
            if resolved in seen:
                continue
            seen.add(resolved)
            if candidate.is_file():
                load_dotenv_file(candidate)
                return candidate
    return None


def parse_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def parse_set_arguments(items: list[str] | None) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in items or []:
        key, separator, value = item.partition("=")
        if not separator or not key:
            raise CliError(f"Invalid key=value item: {item!r}.")
        result[key] = parse_value(value)
    return result


def load_json_file(path: str) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise CliError(f"JSON file {path!r} must contain a top-level object.")
    return data


def load_json_text(raw: str) -> dict[str, Any]:
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise CliError("Inline JSON must contain a top-level object.")
    return data


def build_body(
    *,
    body_file: str | None = None,
    body_json: str | None = None,
    overrides: list[str] | None = None,
    seed: dict[str, Any] | None = None,
) -> tuple[dict[str, Any] | None, bool]:
    body: dict[str, Any] = dict(seed or {})
    user_input = False
    if body_file:
        body.update(load_json_file(body_file))
        user_input = True
    if body_json:
        body.update(load_json_text(body_json))
        user_input = True
    if overrides:
        body.update(parse_set_arguments(overrides))
        user_input = True
    return (body or None, user_input)


def stringify_query_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def encode_query(query: dict[str, Any] | None) -> str:
    if not query:
        return ""
    pairs: list[tuple[str, str]] = []
    for key, value in query.items():
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            for item in value:
                pairs.append((key, stringify_query_value(item)))
        else:
            pairs.append((key, stringify_query_value(value)))
    return urllib.parse.urlencode(pairs)


def resolve_url(base: str, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def request_json(
    *,
    method: str,
    base_url: str,
    path: str,
    api_key: str,
    timeout: float,
    query: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> Any:
    url = resolve_url(base_url, path)
    encoded_query = encode_query(query)
    if encoded_query:
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{encoded_query}"

    headers = {"Authorization": f"Bearer {api_key}"}
    data: bytes | None = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    request = urllib.request.Request(url=url, data=data, headers=headers, method=method.upper())

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            if not raw:
                return {}
            decoded = raw.decode("utf-8")
            try:
                return json.loads(decoded)
            except json.JSONDecodeError:
                return {"raw": decoded}
    except urllib.error.HTTPError as error:
        raw_error = error.read().decode("utf-8", errors="replace")
        payload: Any
        try:
            payload = json.loads(raw_error)
        except json.JSONDecodeError:
            payload = raw_error or error.reason
        raise CliError(f"HTTP {error.code} for {method.upper()} {url}: {json.dumps(payload, ensure_ascii=False)}") from error
    except urllib.error.URLError as error:
        raise CliError(f"Request failed for {method.upper()} {url}: {error.reason}") from error


def should_redact_key(key: str) -> bool:
    normalized = "".join(char for char in key.lower() if char.isalnum() or char == "_")
    return normalized in SECRET_FIELD_NAMES


def redact_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            if should_redact_key(key):
                redacted[key] = REDACTED
                continue
            redacted[key] = redact_payload(value)
        return redacted
    if isinstance(payload, list):
        return [redact_payload(item) for item in payload]
    return payload


def print_output(payload: Any, *, show_secrets: bool) -> None:
    rendered = payload if show_secrets else redact_payload(payload)
    print(json.dumps(rendered, ensure_ascii=False, indent=2, sort_keys=True))


def require_api_key(args: argparse.Namespace) -> str:
    api_key = args.api_key or os.environ.get("PPIO_API_KEY")
    if not api_key:
        raise CliError("Missing API key. Set PPIO_API_KEY or pass --api-key.")
    return api_key


def resolve_surface_base(args: argparse.Namespace, surface: str) -> str:
    if surface == "gpu":
        return args.api_base
    if surface == "core":
        return args.core_api_base
    if surface == "user":
        return args.user_api_base
    raise CliError(f"Unsupported API surface: {surface}")


def common_runtime(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api-key", help="Override PPIO_API_KEY for this command only.")
    parser.add_argument(
        "--api-base",
        default=os.environ.get("PPIO_API_BASE", DEFAULT_GPU_API_BASE),
        help=f"Override the GPU API base URL. Default: {DEFAULT_GPU_API_BASE}",
    )
    parser.add_argument(
        "--core-api-base",
        default=os.environ.get("PPIO_CORE_API_BASE", DEFAULT_CORE_API_BASE),
        help=f"Override the core API base URL. Default: {DEFAULT_CORE_API_BASE}",
    )
    parser.add_argument(
        "--user-api-base",
        default=os.environ.get("PPIO_USER_API_BASE", DEFAULT_USER_API_BASE),
        help=f"Override the user API base URL. Default: {DEFAULT_USER_API_BASE}",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=float(os.environ.get("PPIO_TIMEOUT", str(DEFAULT_TIMEOUT))),
        help=f"Request timeout in seconds. Default: {DEFAULT_TIMEOUT}",
    )
    parser.add_argument(
        "--show-secrets",
        action="store_true",
        help="Disable default redaction for secret-like response fields.",
    )


def fail(error: Exception) -> int:
    print(f"Error: {error}", file=sys.stderr)
    return 1
