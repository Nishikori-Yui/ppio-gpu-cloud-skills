from __future__ import annotations

from .models import EndpointSpec

GROUP = "billing"
GROUP_HELP = "Billing APIs."
ENDPOINTS = {
    "subscription-bills": EndpointSpec("List monthly instance bills.", "GET", "/billing/bill/monthly/list", surface="core"),
    "payg-bills": EndpointSpec("List pay-as-you-go instance bills.", "GET", "/billing/bill/list", surface="core"),
}
