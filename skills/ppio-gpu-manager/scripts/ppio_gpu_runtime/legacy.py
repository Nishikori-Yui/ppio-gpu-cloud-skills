from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, Callable

from .common import CliError
from .registry import ENDPOINT_SPECS


QueryBuilder = Callable[[argparse.Namespace], dict[str, Any] | None]
ArgumentAdder = Callable[[argparse.ArgumentParser], None]
ExecuteFn = Callable[..., Any]


@dataclass(frozen=True)
class GroupRootCompatSpec:
    endpoint_key: str
    add_arguments: ArgumentAdder | None = None
    build_query: QueryBuilder | None = None


def add_instances_list_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--page-size", type=int)
    parser.add_argument("--page-num", type=int)
    parser.add_argument("--name")
    parser.add_argument("--product-name")
    parser.add_argument("--status")


def build_instances_list_query(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "pageSize": args.page_size,
        "pageNum": args.page_num,
        "name": args.name,
        "productName": args.product_name,
        "status": args.status,
    }


ROOT_GROUP_COMPAT_SPECS = {
    "clusters": GroupRootCompatSpec(endpoint_key="clusters:list"),
    "instances": GroupRootCompatSpec(
        endpoint_key="instances:list",
        add_arguments=add_instances_list_arguments,
        build_query=build_instances_list_query,
    ),
}


def add_legacy_alias_parsers(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    add_query_arguments: ArgumentAdder,
    add_body_arguments: ArgumentAdder,
) -> None:
    gpu_products = subparsers.add_parser("gpu-products", help="Compatibility alias for GPU products.")
    gpu_products.add_argument("--cluster-id")
    gpu_products.add_argument("--gpu-num", type=int)
    gpu_products.add_argument("--name")
    gpu_products.add_argument("--cpu-num", type=int)
    gpu_products.add_argument("--memory-size", type=int)
    gpu_products.add_argument("--rootfs-size", type=int)
    gpu_products.add_argument("--billing-mode", choices=["onDemand", "monthly", "spot"])
    gpu_products.set_defaults(mode="legacy", legacy_command="gpu-products")

    cpu_products = subparsers.add_parser("cpu-products", help="Compatibility alias for CPU products.")
    add_query_arguments(cpu_products)
    cpu_products.set_defaults(mode="legacy", legacy_command="cpu-products")

    vpcs = subparsers.add_parser("vpcs", help="Compatibility alias for VPC network listing.")
    vpcs.add_argument("--page-size", type=int)
    vpcs.add_argument("--page-num", type=int)
    vpcs.add_argument("--name")
    vpcs.add_argument("--user")
    vpcs.set_defaults(mode="legacy", legacy_command="vpcs")

    create_vpc = subparsers.add_parser("create-vpc", help="Compatibility alias for VPC network creation.")
    create_vpc.add_argument("--cluster-id")
    create_vpc.add_argument("--name")
    add_body_arguments(create_vpc)
    create_vpc.set_defaults(mode="legacy", legacy_command="create-vpc")

    instance = subparsers.add_parser("instance", help="Compatibility alias for instance details.")
    instance.add_argument("--instance-id", required=True)
    instance.set_defaults(mode="legacy", legacy_command="instance")

    create_instance = subparsers.add_parser("create-instance", help="Compatibility alias for GPU instance creation.")
    add_body_arguments(create_instance)
    create_instance.set_defaults(mode="legacy", legacy_command="create-instance")

    for command_name, help_text in [
        ("start", "Compatibility alias for instance start."),
        ("stop", "Compatibility alias for instance stop."),
        ("restart", "Compatibility alias for instance restart."),
        ("delete", "Compatibility alias for instance delete."),
    ]:
        parser = subparsers.add_parser(command_name, help=help_text)
        parser.add_argument("--instance-id", required=True)
        add_body_arguments(parser)
        parser.set_defaults(mode="legacy", legacy_command=command_name)


def run_legacy_command(args: argparse.Namespace, execute_endpoint_spec: ExecuteFn) -> Any:
    command = args.legacy_command

    if command == "gpu-products":
        query = {
            "clusterId": args.cluster_id,
            "gpuNum": args.gpu_num,
            "name": args.name,
            "cpuNum": args.cpu_num,
            "memorySize": args.memory_size,
            "rootfsSize": args.rootfs_size,
            "billingMode": args.billing_mode,
        }
        return execute_endpoint_spec(ENDPOINT_SPECS["products:gpu"], args, query_overrides=query)

    if command == "cpu-products":
        return execute_endpoint_spec(ENDPOINT_SPECS["products:cpu"], args, query_overrides=args.legacy_query)

    if command == "vpcs":
        query = {
            "pageSize": args.page_size,
            "pageNum": args.page_num,
            "name": args.name,
            "user": args.user,
        }
        return execute_endpoint_spec(ENDPOINT_SPECS["networks:list"], args, query_overrides=query)

    if command == "create-vpc":
        seed: dict[str, Any] = {}
        if args.cluster_id is not None:
            seed["clusterId"] = args.cluster_id
        if args.name is not None:
            seed["name"] = args.name
        return execute_endpoint_spec(ENDPOINT_SPECS["networks:create"], args, body_seed=seed)

    if command == "instance":
        return execute_endpoint_spec(ENDPOINT_SPECS["instances:get"], args, query_overrides={"instanceId": args.instance_id})

    if command == "create-instance":
        return execute_endpoint_spec(ENDPOINT_SPECS["instances:create-gpu"], args)

    if command in {"start", "stop", "restart", "delete"}:
        mapping = {
            "start": "instances:start",
            "stop": "instances:stop",
            "restart": "instances:restart",
            "delete": "instances:delete",
        }
        return execute_endpoint_spec(ENDPOINT_SPECS[mapping[command]], args, body_seed={"instanceId": args.instance_id})

    raise CliError(f"Unsupported legacy command: {command}")
