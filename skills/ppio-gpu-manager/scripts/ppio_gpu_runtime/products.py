from __future__ import annotations

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Any

from .models import EndpointSpec

PRICE_SCALE = Decimal("100000")
PRICE_QUANT = Decimal("0.01")

GROUP = "products"
GROUP_HELP = "GPU and CPU product APIs."


def quantize_cny(value: Decimal) -> Decimal:
    return value.quantize(PRICE_QUANT, rounding=ROUND_HALF_UP)


def format_decimal(value: Decimal) -> str:
    return format(value, "f")


def normalize_price_value(raw: Any) -> Decimal | None:
    if raw in (None, "", "0", 0):
        return None
    try:
        normalized = Decimal(str(raw)) / PRICE_SCALE
    except (InvalidOperation, ValueError):
        return None
    return quantize_cny(normalized)


def enrich_hourly_price(record: dict[str, Any], raw_key: str, numeric_key: str, display_key: str) -> None:
    normalized = normalize_price_value(record.get(raw_key))
    if normalized is None:
        return
    record[numeric_key] = float(normalized)
    record[display_key] = f"CNY {format_decimal(normalized)}/hour"


def enrich_monthly_prices(items: Any) -> Any:
    if not isinstance(items, list):
        return items
    enriched: list[Any] = []
    for item in items:
        if not isinstance(item, dict):
            enriched.append(item)
            continue
        updated = dict(item)
        base_price = normalize_price_value(updated.get("basePrice"))
        price = normalize_price_value(updated.get("price"))
        if base_price is not None:
            updated["basePriceCnyPerMonth"] = float(base_price)
            updated["basePriceDisplay"] = f"CNY {format_decimal(base_price)}/month"
        if price is not None:
            updated["priceCnyPerMonth"] = float(price)
            updated["priceDisplay"] = f"CNY {format_decimal(price)}/month"
        enriched.append(updated)
    return enriched


def enrich_gpu_products(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    items = payload.get("data")
    if not isinstance(items, list):
        return payload
    enriched_items: list[Any] = []
    for item in items:
        if not isinstance(item, dict):
            enriched_items.append(item)
            continue
        updated = dict(item)
        enrich_hourly_price(updated, "price", "priceCnyPerHour", "priceDisplay")
        enrich_hourly_price(updated, "spotPrice", "spotPriceCnyPerHour", "spotPriceDisplay")
        updated["monthlyPrice"] = enrich_monthly_prices(updated.get("monthlyPrice"))
        enriched_items.append(updated)
    updated_payload = dict(payload)
    updated_payload["data"] = enriched_items
    updated_payload["priceNormalization"] = {
        "rule": "raw / 100000",
        "currency": "CNY",
        "source": "validated mapping: RTX 3090 raw 139000 -> CNY 1.39/hour",
    }
    return updated_payload


ENDPOINTS = {
    "gpu": EndpointSpec("List GPU products.", "GET", "/products", response_transform=enrich_gpu_products),
    "cpu": EndpointSpec("List CPU products.", "GET", "/cpu/products"),
}
