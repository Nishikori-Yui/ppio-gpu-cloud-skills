from __future__ import annotations

from .models import EndpointSpec

GROUP = "templates"
GROUP_HELP = "Template APIs."
ENDPOINTS = {
    "create": EndpointSpec("Create a template.", "POST", "/template/create", accepts_body=True, require_user_body=True),
    "update": EndpointSpec("Update a template.", "POST", "/template/update", accepts_body=True, require_user_body=True),
    "delete": EndpointSpec("Delete a template.", "POST", "/template/delete", accepts_body=True, require_user_body=True),
    "list": EndpointSpec("List templates.", "GET", "/templates"),
    "get": EndpointSpec("Get template details.", "GET", "/template"),
}
