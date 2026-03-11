from __future__ import annotations

from .models import EndpointSpec

GROUP = "jobs"
GROUP_HELP = "Job APIs."
ENDPOINTS = {
    "list": EndpointSpec("List jobs.", "GET", "/jobs"),
    "break": EndpointSpec("Force break a job.", "POST", "/job/break", accepts_body=True, require_user_body=True),
}
