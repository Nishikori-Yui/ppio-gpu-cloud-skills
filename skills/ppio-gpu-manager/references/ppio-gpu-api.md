# PPIO GPU API Notes

Read this reference when you need the grouped command mapping, official page URLs, or the documented API path for a specific GPU workflow.

The CLI mapping below is implemented through domain-specific modules under `scripts/ppio_gpu_runtime/`, so new endpoints should be added in the matching API-family module instead of a single monolithic script.

## Official Source Index

- https://ppio.com/docs/gpus/reference-start
- https://ppio.com/docs/gpus/reference-error-code
- https://ppio.com/docs/gpus/reference-get-user-info
- https://ppio.com/docs/gpus/reference-get-bill-subscription
- https://ppio.com/docs/gpus/reference-get-bill-pay-as-you-gpu
- https://ppio.com/docs/gpus/reference-list-clusters
- https://ppio.com/docs/gpus/reference-list-gpu-products
- https://ppio.com/docs/gpus/reference-list-cpu-products
- https://ppio.com/docs/gpus/job/reference-list-jobs
- https://ppio.com/docs/gpus/job/reference-break-job
- https://ppio.com/docs/gpus/vpc/reference-create-vpc
- https://ppio.com/docs/gpus/vpc/reference-list-vpc
- https://ppio.com/docs/gpus/vpc/reference-get-vpc
- https://ppio.com/docs/gpus/vpc/reference-edit-vpc
- https://ppio.com/docs/gpus/vpc/reference-delete-vpc
- https://ppio.com/docs/gpus/instance/reference-create-gpu-instance
- https://ppio.com/docs/gpus/instance/reference-create-cpu-instance
- https://ppio.com/docs/gpus/instance/reference-list-instance
- https://ppio.com/docs/gpus/instance/reference-get-instance
- https://ppio.com/docs/gpus/instance/reference-edit-instance
- https://ppio.com/docs/gpus/instance/reference-start-instance
- https://ppio.com/docs/gpus/instance/reference-stop-instance
- https://ppio.com/docs/gpus/instance/reference-restart-instance
- https://ppio.com/docs/gpus/instance/reference-upgrade-instance
- https://ppio.com/docs/gpus/instance/reference-migrate-instance
- https://ppio.com/docs/gpus/instance/reference-instance-monitor
- https://ppio.com/docs/gpus/instance/reference-renewal-instance
- https://ppio.com/docs/gpus/instance/reference-change-billing-instance
- https://ppio.com/docs/gpus/instance/reference-delete-instance
- https://ppio.com/docs/gpus/instance/reference-set-autorenew
- https://ppio.com/docs/gpus/instance/reference-set-auto-migrate
- https://ppio.com/docs/gpus/template/reference-create-template
- https://ppio.com/docs/gpus/template/reference-update-template
- https://ppio.com/docs/gpus/template/reference-delete-template
- https://ppio.com/docs/gpus/template/reference-list-templates
- https://ppio.com/docs/gpus/template/reference-get-template
- https://ppio.com/docs/gpus/image/reference-save-image
- https://ppio.com/docs/gpus/image/reference-list-image
- https://ppio.com/docs/gpus/image/reference-delete-image
- https://ppio.com/docs/gpus/image/reference-get-image-quota
- https://ppio.com/docs/gpus/image/reference-create-image-prewarm
- https://ppio.com/docs/gpus/image/reference-list-image-prewarm
- https://ppio.com/docs/gpus/image/reference-update-image-prewarm
- https://ppio.com/docs/gpus/image/reference-delete-image-prewarm
- https://ppio.com/docs/gpus/image/reference-list-repository-auths
- https://ppio.com/docs/gpus/endpoint/reference-query-endpoint-limit
- https://ppio.com/docs/gpus/endpoint/reference-create-endpoint
- https://ppio.com/docs/gpus/endpoint/reference-list-endpoint
- https://ppio.com/docs/gpus/endpoint/reference-get-endpoint
- https://ppio.com/docs/gpus/endpoint/reference-update-endpoint
- https://ppio.com/docs/gpus/endpoint/reference-delete-endpoint

## Base URLs

- GPU surface: `https://api.ppio.com/gpu-instance/openapi/v1`
- Core billing and metrics surface: `https://api.ppio.com/openapi/v1`
- User info surface: `https://api.ppio.com/v3`

Environment variables used by the wrapper:

- `PPIO_API_KEY`
- `PPIO_API_BASE`
- `PPIO_CORE_API_BASE`
- `PPIO_USER_API_BASE`
- `PPIO_TIMEOUT`

## Command Mapping

### Base

| CLI command | Method | Path |
| --- | --- | --- |
| `base user-info` | `GET` | `/user` on the user surface |

### Billing

| CLI command | Method | Path |
| --- | --- | --- |
| `billing subscription-bills` | `GET` | `/billing/bill/monthly/list` on the core surface |
| `billing payg-bills` | `GET` | `/billing/bill/list` on the core surface |

### Clusters

| CLI command | Method | Path |
| --- | --- | --- |
| `clusters list` | `GET` | `/clusters` |

### Products

| CLI command | Method | Path |
| --- | --- | --- |
| `products gpu` | `GET` | `/products` |
| `products cpu` | `GET` | `/cpu/products` |

### Jobs

| CLI command | Method | Path |
| --- | --- | --- |
| `jobs list` | `GET` | `/jobs` |
| `jobs break` | `POST` | `/job/break` |

### Networks

| CLI command | Method | Path |
| --- | --- | --- |
| `networks create` | `POST` | `/network/create` |
| `networks list` | `GET` | `/networks` |
| `networks get` | `GET` | `/network` |
| `networks update` | `POST` | `/network/update` |
| `networks delete` | `POST` | `/network/delete` |

### Instances

| CLI command | Method | Path |
| --- | --- | --- |
| `instances create-gpu` | `POST` | `/gpu/instance/create` |
| `instances create-cpu` | `POST` | `/gpu/instance/create` |
| `instances list` | `GET` | `/gpu/instances` |
| `instances get` | `GET` | `/gpu/instance` |
| `instances edit` | `POST` | `/gpu/instance/edit` |
| `instances start` | `POST` | `/gpu/instance/start` |
| `instances stop` | `POST` | `/gpu/instance/stop` |
| `instances restart` | `POST` | `/gpu/instance/restart` |
| `instances upgrade` | `POST` | `/gpu/instance/upgrade` |
| `instances migrate` | `POST` | `/gpu/instance/migrate` |
| `instances monitor` | `GET` | `/metrics/gpu/instance` on the core surface |
| `instances renew` | `POST` | `/gpu/instance/renewInstance` |
| `instances change-billing` | `POST` | `/gpu/instance/transToMonthlyInstance` |
| `instances delete` | `POST` | `/gpu/instance/delete` |
| `instances set-auto-renew` | `POST` | `/gpu/instance/setAutoRenew` |
| `instances set-auto-migrate` | `POST` | `/gpu/instance/setAutoMigrate` |

### Templates

| CLI command | Method | Path |
| --- | --- | --- |
| `templates create` | `POST` | `/template/create` |
| `templates update` | `POST` | `/template/update` |
| `templates delete` | `POST` | `/template/delete` |
| `templates list` | `GET` | `/templates` |
| `templates get` | `GET` | `/template` |

### Images

| CLI command | Method | Path |
| --- | --- | --- |
| `images save` | `POST` | `/job/save/image` |
| `images list` | `GET` | `/images` |
| `images delete` | `POST` | `/image/delete` |
| `images quota` | `GET` | `/image/prewarm/quota` |
| `images prewarm-create` | `POST` | `/image/prewarm` |
| `images prewarm-list` | `GET` | `/image/prewarm` |
| `images prewarm-update` | `POST` | `/image/prewarm/edit` |
| `images prewarm-delete` | `POST` | `/image/prewarm/delete` |
| `images repository-auths` | `GET` | `/repository/auths` |

### Endpoints

| CLI command | Method | Path |
| --- | --- | --- |
| `endpoints limits` | `GET` | `/endpoint/limit` |
| `endpoints create` | `POST` | `/endpoint/create` |
| `endpoints list` | `GET` | `/endpoints` |
| `endpoints get` | `GET` | `/endpoint` |
| `endpoints update` | `POST` | `/endpoint/update` |
| `endpoints delete` | `POST` | `/endpoint/delete` |

## Request Shapes

- Read-only commands accept repeated `--query key=value` parameters when the official docs use query strings.
- Body-based commands accept `--body-file`, `--body-json`, and repeated `--set key=value`.
- `products gpu` keeps the repository-local readable price enrichment for hourly and monthly CNY fields.
- `instances create-gpu` seeds `kind=gpu`, while `instances create-cpu` seeds `kind=cpu`.

## Compatibility Aliases

The wrapper preserves legacy flat commands for the older minimal surface:

- `clusters`
- `gpu-products`
- `vpcs`
- `create-vpc`
- `instances`
- `instance`
- `create-instance`
- `start`
- `stop`
- `restart`
- `delete`

These aliases map onto the grouped command tree and keep the previous shell usage valid.
