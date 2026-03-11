from __future__ import annotations

from .models import EndpointSpec

GROUP = "endpoints"
GROUP_HELP = "Endpoint APIs."
ENDPOINTS = {
    "limits": EndpointSpec("Get endpoint parameter limits.", "GET", "/endpoint/limit"),
    "create": EndpointSpec("Create an endpoint.", "POST", "/endpoint/create", accepts_body=True, require_user_body=True),
    "list": EndpointSpec("List endpoints.", "GET", "/endpoints"),
    "get": EndpointSpec("Get endpoint details.", "GET", "/endpoint"),
    "update": EndpointSpec("Update an endpoint.", "POST", "/endpoint/update", accepts_body=True, require_user_body=True),
    "delete": EndpointSpec("Delete an endpoint.", "POST", "/endpoint/delete", accepts_body=True, require_user_body=True),
}
