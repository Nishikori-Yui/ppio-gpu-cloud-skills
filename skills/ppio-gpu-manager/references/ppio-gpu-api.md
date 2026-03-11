# PPIO GPU API Notes

Read this reference when you need exact request fields or when a lifecycle operation fails and you need to verify the documented contract.

## Official Sources

- https://ppio.com/docs/gpus/reference-start
- https://ppio.com/docs/gpus/reference-list-clusters
- https://ppio.com/docs/gpus/reference-list-gpu-products
- https://ppio.com/docs/gpus/vpc/reference-create-vpc
- https://ppio.com/docs/gpus/vpc/reference-list-vpc
- https://ppio.com/docs/gpus/instance/reference-create-gpu-instance
- https://ppio.com/docs/gpus/instance/reference-list-instance
- https://ppio.com/docs/gpus/instance/reference-get-instance
- https://ppio.com/docs/gpus/instance/reference-start-instance
- https://ppio.com/docs/gpus/instance/reference-stop-instance
- https://ppio.com/docs/gpus/instance/reference-restart-instance
- https://ppio.com/docs/gpus/instance/reference-delete-instance

## Base URL and Auth

- Base URL: `https://api.ppio.com/gpu-instance/openapi/v1`
- Header: `Authorization: Bearer <API_KEY>`
- POST header: `Content-Type: application/json`
- The wrapper auto-loads a local `.env` file when present and falls back to the process environment.
- Resolution order for files is: skill-local `.env`, then current-working-directory `.env` search upward.

## Wrapped Endpoints

| Skill command | Method | Path |
| --- | --- | --- |
| `clusters` | `GET` | `/clusters` |
| `gpu-products` | `GET` | `/products` |
| `vpcs` | `GET` | `/networks` |
| `create-vpc` | `POST` | `/network/create` |
| `instances` | `GET` | `/gpu/instances` |
| `instance` | `GET` | `/gpu/instance` |
| `create-instance` | `POST` | `/gpu/instance/create` |
| `start` | `POST` | `/gpu/instance/start` |
| `stop` | `POST` | `/gpu/instance/stop` |
| `restart` | `POST` | `/gpu/instance/restart` |
| `delete` | `POST` | `/gpu/instance/delete` |

## Cluster Discovery

`GET /clusters` returns a `data` array with at least:

- `id`
- `name`
- `availableGpuType`
- `supportNetworkStorage`
- `supportInstanceNetwork`

Use cluster discovery before choosing `clusterId` or deciding whether VPC is supported.

## GPU Product Discovery

`GET /products` supports the following useful filters:

- `clusterId`
- `gpuNum`
- `name`
- `cpuNum`
- `memorySize`
- `rootfsSize`
- `billingMode`

Each product record includes at least:

- `id`
- `name`
- `availableDeploy`

Use a product with `availableDeploy=true` before attempting instance creation.

The wrapper enriches product pricing with repository-local readable fields:

- `priceCnyPerHour`
- `priceDisplay`
- `spotPriceCnyPerHour`
- `spotPriceDisplay`
- `monthlyPrice[*].basePriceCnyPerMonth`
- `monthlyPrice[*].priceCnyPerMonth`

Normalization rule used by the wrapper:

```text
raw price / 100000 = CNY value
```

This rule is based on a validated mapping where raw `139000` for `RTX 3090 24GB` corresponds to `CNY 1.39/hour`.

## VPC Notes

### Create VPC

`POST /network/create`

Documented request fields:

```json
{
  "clusterId": "string",
  "name": "string"
}
```

### List VPCs

`GET /networks`

Useful filters:

- `pageSize`
- `pageNum`
- `name`
- `user`

## Create GPU Instance

`POST /gpu/instance/create`

Most common top-level request fields:

- `name`
- `productId`
- `gpuNum`
- `rootfsSize`
- `imageUrl`
- `clusterId`
- `networkId`
- `billingMode`
- `kind`

Optional structured fields:

- `envs`: array of `{ "key": "...", "value": "..." }`
- `tools`: array of `{ "name": "Jupyter", "port": "8888", "type": "http" }`
- `volumeMounts`: array of `{ "id": "network-storage-id", "mountPath": "/network" }`

Example request body:

```json
{
  "name": "trainer-a10",
  "productId": "prod_xxx",
  "gpuNum": 1,
  "rootfsSize": 80,
  "imageUrl": "nvcr.io/nvidia/pytorch:24.02-py3",
  "clusterId": "",
  "networkId": "",
  "kind": "gpu",
  "billingMode": "onDemand",
  "envs": [
    {
      "key": "EXAMPLE_ENV",
      "value": "example"
    }
  ]
}
```

## Instance Inspection

### List Instances

`GET /gpu/instances`

Useful filters:

- `pageSize`
- `pageNum`
- `name`
- `productName`
- `status`

### Get Instance

`GET /gpu/instance`

Required query parameter:

- `instanceId`

Useful response fields:

- `id`
- `name`
- `status`
- `clusterId`
- `clusterName`
- `productId`
- `productName`
- `sshCommand`
- `password`
- `network`
- `portMappings`
- `tools`
- `statusError`

## Instance Status Values

- `toCreate`
- `creating`
- `pulling`
- `running`
- `toStart`
- `starting`
- `toStop`
- `stopping`
- `exited`
- `toRestart`
- `restarting`
- `toRemove`
- `removing`
- `removed`
- `toReset`
- `resetting`
- `migrating`
- `freezing`

## Lifecycle Request Body

The documented request body for start, stop, restart, and delete is:

```json
{
  "instanceId": "string"
}
```

## Wrapper Examples

```bash
export PPIO_API_KEY="your-api-key"
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py clusters
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py gpu-products --billing-mode onDemand
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instances --status running
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py instance --instance-id "ins_xxx"
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py create-instance --body-file /absolute/path/spec.json
python3 skills/ppio-gpu-manager/scripts/ppio_gpu.py restart --instance-id "ins_xxx"
```
