from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class FlightPayload(BaseModel):
    codigo: Any
    origen: str = ""
    destino: str = ""
    horaSalida: str = ""
    precioBase: float = 0.0
    pasajeros: int = 0
    prioridad: int | str = "MEDIA"
    promocion: float | bool = 0.0
    alerta: str | bool = "NORMAL"


class FlightUpdatePayload(BaseModel):
    origen: str = ""
    destino: str = ""
    horaSalida: str = ""
    precioBase: float = 0.0
    pasajeros: int = 0
    prioridad: int | str = "MEDIA"
    promocion: float | bool = 0.0
    alerta: str | bool = "NORMAL"


class StressModePayload(BaseModel):
    enabled: bool


class VersionPayload(BaseModel):
    name: str = Field(..., min_length=1)
    overwrite: bool = False


class FilePathPayload(BaseModel):
    path: str = Field(..., min_length=1)


class QueueProcessPayload(BaseModel):
    limit: Optional[int] = Field(default=None, ge=1)
