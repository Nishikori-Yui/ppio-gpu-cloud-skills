from __future__ import annotations

from .models import EndpointSpec

GROUP = "clusters"
GROUP_HELP = "Cluster discovery APIs."
ENDPOINTS = {
    "list": EndpointSpec("List clusters.", "GET", "/clusters"),
}
