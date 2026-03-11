from __future__ import annotations

from .models import EndpointSpec

GROUP = "images"
GROUP_HELP = "Image and image prewarm APIs."
ENDPOINTS = {
    "save": EndpointSpec("Save an image.", "POST", "/job/save/image", accepts_body=True, require_user_body=True),
    "list": EndpointSpec("List images.", "GET", "/images"),
    "delete": EndpointSpec("Delete an image.", "POST", "/image/delete", accepts_body=True, require_user_body=True),
    "quota": EndpointSpec("Get image prewarm quota.", "GET", "/image/prewarm/quota"),
    "prewarm-create": EndpointSpec("Create an image prewarm task.", "POST", "/image/prewarm", accepts_body=True, require_user_body=True),
    "prewarm-list": EndpointSpec("List image prewarm tasks.", "GET", "/image/prewarm"),
    "prewarm-update": EndpointSpec("Update an image prewarm task.", "POST", "/image/prewarm/edit", accepts_body=True, require_user_body=True),
    "prewarm-delete": EndpointSpec("Delete an image prewarm task.", "POST", "/image/prewarm/delete", accepts_body=True, require_user_body=True),
    "repository-auths": EndpointSpec("List image repository auths.", "GET", "/repository/auths"),
}
