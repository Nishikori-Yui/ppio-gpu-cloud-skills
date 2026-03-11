from __future__ import annotations

from .models import EndpointSpec

GROUP = "base"
GROUP_HELP = "Account information APIs."
ENDPOINTS = {
    "user-info": EndpointSpec("Get account information.", "GET", "/user", surface="user"),
}
