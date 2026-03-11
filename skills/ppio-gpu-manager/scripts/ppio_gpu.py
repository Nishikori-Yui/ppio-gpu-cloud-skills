#!/usr/bin/env python3

from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_API_BASE = "https://api.ppio.com/gpu-instance/openapi/v1"
DEFAULT_TIMEOUT = 30.0
PRICE_SCALE = Decimal("100000")
PRICE_QUANT = Decimal("0.01")
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


def quantize_cny(value: Decimal) -> Decimal:
    return value.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)


def format_decimal(value: Decimal) -> str:
    return format(value, "f")


def normalize_price_value(raw: Any) -> Decimal | None:
    if raw in (None, "", "0", 0):
        return None
    try:
        normalized = Decimal(str(raw)) / PRICE_SCALE
    except (InvalidOperation, ValueError):
        return None
    return quantize_cny(normalized)


def enrich_hourly_price(record: dict[str, Any], raw_key: str, numeric_key: str, display_key: str) -> None:
    normalized = normalize_price_value(record.get(raw_key))
    if normalized is None:
        return
    record[numeric_key] = float(normalized)
    record[display_key] = f"CNY {format_decimal(normalized)}/hour"


def enrich_monthly_prices(items: Any) -> Any:
    if not isinstance(items, list):
        return items
    enriched: list[Any] = []
    for item in items:
        if not isinstance(item, dict):
            enriched.append(item)
            continue
        updated = dict(item)
        base_price = normalize_price_value(updated.get("basePrice"))
        price = normalize_price_value(updated.get("price"))
        if base_price is not None:
            updated["basePriceCnyPerMonth"] = float(base_price)
            updated["basePriceDisplay"] = f"CNY {format_decimal(base_price)}/month"
        if price is not None:
            updated["priceCnyPerMonth"] = float(price)
            updated["priceDisplay"] = f"CNY {format_decimal(price)}/month"
        enriched.append(updated)
    return enriched


def enrich_gpu_products(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    items = payload.get("data")
    if not isinstance(items, list):
        return payload
    enriched_items: list[Any] = []
    for item in items:
        if not isinstance(item, dict):
            enriched_items.append(item)
            continue
        updated = dict(item)
        enrich_hourly_price(updated, "price", "priceCnyPerHour", "priceDisplay")
        enrich_hourly_price(updated, "spotPrice", "spotPriceCnyPerHour", "spotPriceDisplay")
        updated["monthlyPrice"] = enrich_monthly_prices(updated.get("monthlyPrice"))
        enriched_items.append(updated)
    updated_payload = dict(payload)
    updated_payload["data"] = enriched_items
    updated_payload["priceNormalization"] = {
        "rule": "raw / 100000",
        "currency": "CNY",
        "source": "validated mapping: RTX 3090 raw 139000 -> CNY 1.39/hour",
    }
    return updated_payload


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


def bootstrap_environment() -> Path | None:
    roots = [Path(__file__).resolve().parent, Path.cwd()]
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


def parse_set_arguments(items: list[str] | None) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for item in items or []:
        key, separator, value = item.partition("=")
        if not separator or not key:
            raise CliError(f"Invalid --set value: {item!r}. Expected key=value.")
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
) -> dict[str, Any] | None:
    body: dict[str, Any] = dict(seed or {})
    if body_file:
        body.update(load_json_file(body_file))
    if body_json:
        body.update(load_json_text(body_json))
    if overrides:
        body.update(parse_set_arguments(overrides))
    return body or None


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


def print_output(payload: Any, *, show_secrets: bool) -> None:
    rendered = payload if show_secrets else redact_payload(payload)
    print(json.dumps(rendered, ensure_ascii=False, indent=2, sort_keys=True))


def require_api_key(args: argparse.Namespace) -> str:
    api_key = args.api_key or os.environ.get("PPIO_API_KEY")
    if not api_key:
        raise CliError("Missing API key. Set PPIO_API_KEY or pass --api-key.")
    return api_key


def common_runtime(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--api-key", help="Override PPIO_API_KEY for this command only.")
    parser.add_argument(
        "--api-base",
        default=os.environ.get("PPIO_API_BASE", DEFAULT_API_BASE),
        help=f"Override the API base URL. Default: {DEFAULT_API_BASE}",
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage PPIO GPU resources through the documented OpenAPI.")
    common_runtime(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("clusters", help="List available PPIO clusters.")

    gpu_products = subparsers.add_parser("gpu-products", help="List GPU products.")
    gpu_products.add_argument("--cluster-id")
    gpu_products.add_argument("--gpu-num", type=int)
    gpu_products.add_argument("--name")
    gpu_products.add_argument("--cpu-num", type=int)
    gpu_products.add_argument("--memory-size", type=int)
    gpu_products.add_argument("--rootfs-size", type=int)
    gpu_products.add_argument("--billing-mode", choices=["onDemand", "monthly", "spot"])

    vpcs = subparsers.add_parser("vpcs", help="List VPC networks.")
    vpcs.add_argument("--page-size", type=int)
    vpcs.add_argument("--page-num", type=int)
    vpcs.add_argument("--name")
    vpcs.add_argument("--user")

    create_vpc = subparsers.add_parser("create-vpc", help="Create a VPC network.")
    create_vpc.add_argument("--cluster-id")
    create_vpc.add_argument("--name")
    create_vpc.add_argument("--body-file")
    create_vpc.add_argument("--body-json")
    create_vpc.add_argument("--set", action="append", default=[], help="Override request fields as key=value.")

    instances = subparsers.add_parser("instances", help="List GPU instances.")
    instances.add_argument("--page-size", type=int)
    instances.add_argument("--page-num", type=int)
    instances.add_argument("--name")
    instances.add_argument("--product-name")
    instances.add_argument("--status")

    instance = subparsers.add_parser("instance", help="Get instance details.")
    instance.add_argument("--instance-id", required=True)

    create_instance = subparsers.add_parser("create-instance", help="Create a GPU instance from a JSON spec.")
    create_instance.add_argument("--body-file")
    create_instance.add_argument("--body-json")
    create_instance.add_argument("--set", action="append", default=[], help="Set top-level request fields as key=value.")

    for command_name, help_text in [
        ("start", "Start an instance."),
        ("stop", "Stop an instance."),
        ("restart", "Restart an instance."),
        ("delete", "Delete an instance."),
    ]:
        command = subparsers.add_parser(command_name, help=help_text)
        command.add_argument("--instance-id", required=True)
        command.add_argument("--body-file")
        command.add_argument("--body-json")
        command.add_argument("--set", action="append", default=[], help="Override request fields as key=value.")

    request = subparsers.add_parser("request", help="Send a generic request to the PPIO GPU API.")
    request.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    request.add_argument("path", help="Relative API path such as /clusters, or an absolute URL.")
    request.add_argument("--query", action="append", default=[], help="Add query parameters as key=value.")
    request.add_argument("--body-file")
    request.add_argument("--body-json")
    request.add_argument("--set", action="append", default=[], help="Override request fields as key=value.")

    return parser


def run_command(args: argparse.Namespace) -> Any:
    api_key = require_api_key(args)
    base_url = args.api_base
    timeout = args.timeout

    if args.command == "clusters":
        return request_json(method="GET", base_url=base_url, path="/clusters", api_key=api_key, timeout=timeout)

    if args.command == "gpu-products":
        query = {
            "clusterId": args.cluster_id,
            "gpuNum": args.gpu_num,
            "name": args.name,
            "cpuNum": args.cpu_num,
            "memorySize": args.memory_size,
            "rootfsSize": args.rootfs_size,
            "billingMode": args.billing_mode,
        }
        payload = request_json(method="GET", base_url=base_url, path="/products", api_key=api_key, timeout=timeout, query=query)
        return enrich_gpu_products(payload)

    if args.command == "vpcs":
        query = {
            "pageSize": args.page_size,
            "pageNum": args.page_num,
            "name": args.name,
            "user": args.user,
        }
        return request_json(method="GET", base_url=base_url, path="/networks", api_key=api_key, timeout=timeout, query=query)

    if args.command == "create-vpc":
        seed = {}
        if args.cluster_id is not None:
            seed["clusterId"] = args.cluster_id
        if args.name is not None:
            seed["name"] = args.name
        body = build_body(body_file=args.body_file, body_json=args.body_json, overrides=args.set, seed=seed)
        if not body:
            raise CliError("create-vpc requires --cluster-id/--name, --body-file, --body-json, or --set.")
        return request_json(method="POST", base_url=base_url, path="/network/create", api_key=api_key, timeout=timeout, body=body)

    if args.command == "instances":
        query = {
            "pageSize": args.page_size,
            "pageNum": args.page_num,
            "name": args.name,
            "productName": args.product_name,
            "status": args.status,
        }
        return request_json(method="GET", base_url=base_url, path="/gpu/instances", api_key=api_key, timeout=timeout, query=query)

    if args.command == "instance":
        return request_json(
            method="GET",
            base_url=base_url,
            path="/gpu/instance",
            api_key=api_key,
            timeout=timeout,
            query={"instanceId": args.instance_id},
        )

    if args.command == "create-instance":
        body = build_body(body_file=args.body_file, body_json=args.body_json, overrides=args.set)
        if not body:
            raise CliError("create-instance requires --body-file, --body-json, or at least one --set.")
        return request_json(
            method="POST",
            base_url=base_url,
            path="/gpu/instance/create",
            api_key=api_key,
            timeout=timeout,
            body=body,
        )

    if args.command in {"start", "stop", "restart", "delete"}:
        endpoint_map = {
            "start": "/gpu/instance/start",
            "stop": "/gpu/instance/stop",
            "restart": "/gpu/instance/restart",
            "delete": "/gpu/instance/delete",
        }
        seed = {"instanceId": args.instance_id}
        body = build_body(body_file=args.body_file, body_json=args.body_json, overrides=args.set, seed=seed)
        return request_json(
            method="POST",
            base_url=base_url,
            path=endpoint_map[args.command],
            api_key=api_key,
            timeout=timeout,
            body=body,
        )

    if args.command == "request":
        query = parse_set_arguments(args.query)
        body = build_body(body_file=args.body_file, body_json=args.body_json, overrides=args.set)
        return request_json(
            method=args.method,
            base_url=base_url,
            path=args.path,
            api_key=api_key,
            timeout=timeout,
            query=query,
            body=body,
        )

    raise CliError(f"Unsupported command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    bootstrap_environment()
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload = run_command(args)
        print_output(payload, show_secrets=args.show_secrets)
        return 0
    except CliError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
