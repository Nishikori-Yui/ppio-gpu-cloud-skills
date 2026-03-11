from __future__ import annotations

from . import base, billing, clusters, endpoints, images, instances, jobs, networks, products, templates
from .models import EndpointSpec

DOMAIN_MODULES = (
    base,
    billing,
    clusters,
    products,
    jobs,
    networks,
    instances,
    templates,
    images,
    endpoints,
)


def build_registry() -> tuple[dict[str, EndpointSpec], dict[str, list[str]], dict[str, str]]:
    endpoint_specs: dict[str, EndpointSpec] = {}
    group_actions: dict[str, list[str]] = {}
    group_help: dict[str, str] = {}

    for module in DOMAIN_MODULES:
        group = module.GROUP
        actions: list[str] = []
        for action, spec in module.ENDPOINTS.items():
            endpoint_key = f"{group}:{action}"
            if endpoint_key in endpoint_specs:
                raise ValueError(f"Duplicate endpoint key: {endpoint_key}")
            endpoint_specs[endpoint_key] = spec
            actions.append(action)
        group_actions[group] = actions
        group_help[group] = module.GROUP_HELP

    return endpoint_specs, group_actions, group_help


ENDPOINT_SPECS, GROUP_ACTIONS, GROUP_HELP = build_registry()
