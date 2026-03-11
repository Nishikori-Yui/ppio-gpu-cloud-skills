from __future__ import annotations

import argparse
from typing import Any

from .common import (
    CliError,
    bootstrap_environment,
    build_body,
    common_runtime,
    fail,
    parse_set_arguments,
    print_output,
    request_json,
    require_api_key,
    resolve_surface_base,
)
from .legacy import ROOT_GROUP_COMPAT_SPECS, add_legacy_alias_parsers, run_legacy_command
from .models import EndpointSpec
from .registry import ENDPOINT_SPECS, GROUP_ACTIONS, GROUP_HELP


def add_query_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--query", action="append", default=[], help="Add query parameters as key=value.")


def add_body_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--body-file", help="Load the request body from a JSON file.")
    parser.add_argument("--body-json", help="Inline request body as a JSON object.")
    parser.add_argument("--set", action="append", default=[], help="Override request body fields as key=value.")


def add_group_command_parsers(subparsers: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    for group, actions in GROUP_ACTIONS.items():
        group_parser = subparsers.add_parser(group, help=GROUP_HELP[group])
        root_compat = ROOT_GROUP_COMPAT_SPECS.get(group)
        if root_compat and root_compat.add_arguments is not None:
            root_compat.add_arguments(group_parser)
        if root_compat:
            group_parser.set_defaults(mode="grouped", endpoint_key=root_compat.endpoint_key, grouped_query_builder=root_compat.build_query)
        group_subparsers = group_parser.add_subparsers(dest=f"{group}_action", required=root_compat is None)

        for action in actions:
            endpoint_key = f"{group}:{action}"
            spec = ENDPOINT_SPECS[endpoint_key]
            parser = group_subparsers.add_parser(action, help=spec.help)
            parser.set_defaults(
                endpoint_key=endpoint_key,
                mode="grouped",
                grouped_query_builder=root_compat.build_query if root_compat and action == "list" else None,
            )
            if root_compat and action == "list" and root_compat.add_arguments is not None:
                root_compat.add_arguments(parser)
            if spec.method == "GET":
                add_query_arguments(parser)
            if spec.accepts_body:
                add_body_arguments(parser)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the full official PPIO GPU API through a grouped CLI wrapper.")
    common_runtime(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_group_command_parsers(subparsers)
    add_legacy_alias_parsers(subparsers, add_query_arguments, add_body_arguments)

    request = subparsers.add_parser("request", help="Send a generic request to the official GPU API surfaces.")
    request.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    request.add_argument("path", help="Relative API path such as /clusters, or an absolute URL.")
    request.add_argument("--surface", choices=["gpu", "core", "user"], default="gpu", help="Select the default API surface for relative paths.")
    add_query_arguments(request)
    add_body_arguments(request)
    request.set_defaults(mode="request")

    return parser


def execute_endpoint_spec(
    spec: EndpointSpec,
    args: argparse.Namespace,
    *,
    query_overrides: dict[str, Any] | None = None,
    body_seed: dict[str, Any] | None = None,
) -> Any:
    api_key = require_api_key(args)
    base_url = resolve_surface_base(args, spec.surface)
    timeout = args.timeout
    query = dict(query_overrides or {})
    if spec.method == "GET":
        query.update(parse_set_arguments(getattr(args, "query", [])))

    body: dict[str, Any] | None = None
    if spec.accepts_body:
        seed = dict(spec.default_body or {})
        seed.update(body_seed or {})
        body, user_input = build_body(
            body_file=getattr(args, "body_file", None),
            body_json=getattr(args, "body_json", None),
            overrides=getattr(args, "set", None),
            seed=seed,
        )
        if spec.require_user_body and not user_input and not body_seed:
            raise CliError(f"{args.command} requires --body-file, --body-json, or at least one --set.")

    payload = request_json(
        method=spec.method,
        base_url=base_url,
        path=spec.path,
        api_key=api_key,
        timeout=timeout,
        query=query or None,
        body=body,
    )
    if spec.response_transform is not None:
        return spec.response_transform(payload)
    return payload


def run_grouped_command(args: argparse.Namespace) -> Any:
    query_builder = getattr(args, "grouped_query_builder", None)
    query_overrides = query_builder(args) if callable(query_builder) else None
    return execute_endpoint_spec(ENDPOINT_SPECS[getattr(args, "endpoint_key", "")], args, query_overrides=query_overrides)


def run_request_command(args: argparse.Namespace) -> Any:
    api_key = require_api_key(args)
    base_url = resolve_surface_base(args, args.surface)
    query = parse_set_arguments(args.query)
    body, _ = build_body(body_file=args.body_file, body_json=args.body_json, overrides=args.set)
    return request_json(
        method=args.method,
        base_url=base_url,
        path=args.path,
        api_key=api_key,
        timeout=args.timeout,
        query=query or None,
        body=body,
    )


def run_command(args: argparse.Namespace) -> Any:
    if args.mode == "grouped":
        return run_grouped_command(args)
    if args.mode == "legacy":
        if hasattr(args, "query"):
            args.legacy_query = parse_set_arguments(args.query)
        else:
            args.legacy_query = None
        return run_legacy_command(args, execute_endpoint_spec)
    if args.mode == "request":
        return run_request_command(args)
    raise CliError("Unsupported command mode.")


def main(argv: list[str] | None = None) -> int:
    bootstrap_environment(__file__)
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload = run_command(args)
        print_output(payload, show_secrets=args.show_secrets)
        return 0
    except CliError as error:
        return fail(error)
