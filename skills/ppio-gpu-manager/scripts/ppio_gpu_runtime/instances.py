from __future__ import annotations

from .models import EndpointSpec

GROUP = "instances"
GROUP_HELP = "Instance APIs."
ENDPOINTS = {
    "create-gpu": EndpointSpec("Create a GPU instance.", "POST", "/gpu/instance/create", accepts_body=True, default_body={"kind": "gpu"}, require_user_body=True),
    "create-cpu": EndpointSpec("Create a CPU instance.", "POST", "/gpu/instance/create", accepts_body=True, default_body={"kind": "cpu"}, require_user_body=True),
    "list": EndpointSpec("List instances.", "GET", "/gpu/instances"),
    "get": EndpointSpec("Get instance details.", "GET", "/gpu/instance"),
    "edit": EndpointSpec("Edit an instance.", "POST", "/gpu/instance/edit", accepts_body=True, require_user_body=True),
    "start": EndpointSpec("Start an instance.", "POST", "/gpu/instance/start", accepts_body=True, require_user_body=True),
    "stop": EndpointSpec("Stop an instance.", "POST", "/gpu/instance/stop", accepts_body=True, require_user_body=True),
    "restart": EndpointSpec("Restart an instance.", "POST", "/gpu/instance/restart", accepts_body=True, require_user_body=True),
    "upgrade": EndpointSpec("Upgrade an instance.", "POST", "/gpu/instance/upgrade", accepts_body=True, require_user_body=True),
    "migrate": EndpointSpec("Migrate an instance.", "POST", "/gpu/instance/migrate", accepts_body=True, require_user_body=True),
    "monitor": EndpointSpec("Get instance monitor data.", "GET", "/metrics/gpu/instance", surface="core"),
    "renew": EndpointSpec("Renew a monthly instance.", "POST", "/gpu/instance/renewInstance", accepts_body=True, require_user_body=True),
    "change-billing": EndpointSpec("Convert a pay-as-you-go instance to monthly billing.", "POST", "/gpu/instance/transToMonthlyInstance", accepts_body=True, require_user_body=True),
    "delete": EndpointSpec("Delete an instance.", "POST", "/gpu/instance/delete", accepts_body=True, require_user_body=True),
    "set-auto-renew": EndpointSpec("Set auto renew for a monthly instance.", "POST", "/gpu/instance/setAutoRenew", accepts_body=True, require_user_body=True),
    "set-auto-migrate": EndpointSpec("Set the auto migrate policy for an instance.", "POST", "/gpu/instance/setAutoMigrate", accepts_body=True, require_user_body=True),
}
