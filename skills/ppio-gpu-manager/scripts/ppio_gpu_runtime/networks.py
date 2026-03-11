from __future__ import annotations

from .models import EndpointSpec

GROUP = "networks"
GROUP_HELP = "VPC network APIs."
ENDPOINTS = {
    "create": EndpointSpec("Create a VPC network.", "POST", "/network/create", accepts_body=True, require_user_body=True),
    "list": EndpointSpec("List VPC networks.", "GET", "/networks"),
    "get": EndpointSpec("Get VPC network details.", "GET", "/network"),
    "update": EndpointSpec("Update a VPC network.", "POST", "/network/update", accepts_body=True, require_user_body=True),
    "delete": EndpointSpec("Delete a VPC network.", "POST", "/network/delete", accepts_body=True, require_user_body=True),
}
