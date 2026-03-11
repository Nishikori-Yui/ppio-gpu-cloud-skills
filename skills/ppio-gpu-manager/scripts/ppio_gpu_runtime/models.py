from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


TransformFn = Callable[[Any], Any]


@dataclass(frozen=True)
class EndpointSpec:
    help: str
    method: str
    path: str
    surface: str = "gpu"
    accepts_body: bool = False
    response_transform: TransformFn | None = None
    default_body: dict[str, Any] | None = None
    require_user_body: bool = False
