from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


_PRIORITY_MAP: dict[str, str] = {
    "1": "ALTA",
    "2": "MEDIA",
    "3": "BAJA",
    "ALTA": "ALTA",
    "MEDIA": "MEDIA",
    "BAJA": "BAJA",
}


@dataclass
class FlightFormData:
    codigo: Any
    origen: str
    destino: str
    hora_salida: str
    precio_base: Any
    pasajeros: Any
    prioridad: Any = "MEDIA"
    promocion: Any = 0.0
    alerta: Any = "NORMAL"

    def to_api_payload(self) -> dict[str, Any]:
        return {
            "codigo": self.codigo,
            "origen": str(self.origen).strip(),
            "destino": str(self.destino).strip(),
            "horaSalida": str(self.hora_salida).strip(),
            "precioBase": _to_float(self.precio_base, field_name="precio_base"),
            "pasajeros": _to_int(self.pasajeros, field_name="pasajeros"),
            "prioridad": _normalize_priority(self.prioridad),
            "promocion": _normalize_promotion(self.promocion),
            "alerta": _normalize_alert(self.alerta),
        }

@dataclass
class FlightFormDataUpdate:
    origen: str
    destino: str
    hora_salida: str
    precio_base: Any
    pasajeros: Any
    prioridad: Any = "MEDIA"
    promocion: Any = 0.0
    alerta: Any = "NORMAL"

    def to_api_payload(self) -> dict[str, Any]:
        return {
            "origen": str(self.origen).strip(),
            "destino": str(self.destino).strip(),
            "horaSalida": str(self.hora_salida).strip(),
            "precioBase": _to_float(self.precio_base, field_name="precio_base"),
            "pasajeros": _to_int(self.pasajeros, field_name="pasajeros"),
            "prioridad": _normalize_priority(self.prioridad),
            "promocion": _normalize_promotion(self.promocion),
            "alerta": _normalize_alert(self.alerta),
        }

@dataclass
class QueueProcessFormData:
    limit: Optional[Any] = None

    def to_api_payload(self) -> dict[str, Any]:
        if self.limit in (None, ""):
            return {"limit": None}

        parsed_limit = _to_int(self.limit, field_name="limit")
        if parsed_limit <= 0:
            raise ValueError("limit debe ser mayor a 0")
        return {"limit": parsed_limit}


@dataclass
class VersionFormData:
    name: str
    overwrite: bool = False

    def to_api_payload(self) -> dict[str, Any]:
        clean_name = str(self.name).strip()
        if not clean_name:
            raise ValueError("name no puede estar vacio")
        return {
            "name": clean_name,
            "overwrite": bool(self.overwrite),
        }


@dataclass
class FilePathFormData:
    path: str

    def to_api_payload(self) -> dict[str, Any]:
        clean_path = str(self.path).strip()
        if not clean_path:
            raise ValueError("path no puede estar vacio")
        return {"path": clean_path}


@dataclass
class StressModeFormData:
    enabled: bool

    def to_api_payload(self) -> dict[str, Any]:
        return {"enabled": bool(self.enabled)}


def _to_float(value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} debe ser numerico") from exc


def _to_int(value: Any, field_name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} debe ser entero") from exc


def _normalize_priority(value: Any) -> str:
    text = str(value).strip().upper()
    return _PRIORITY_MAP.get(text, "MEDIA")


def _normalize_promotion(value: Any) -> float | bool:
    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if text in {"true", "si", "sí"}:
        return True
    if text in {"false", "no"}:
        return False
    return _to_float(value, field_name="promocion")


def _normalize_alert(value: Any) -> str | bool:
    if isinstance(value, bool):
        return value

    text = str(value).strip().upper()
    if text in {"ALERTA", "NORMAL"}:
        return text
    if text in {"TRUE", "SI", "SÍ"}:
        return True
    if text in {"FALSE", "NO"}:
        return False
    return "NORMAL"


# ============================================================================
# Estructuras para visualización de árboles (respuestas de render-data)
# ============================================================================

@dataclass
class TreeNodeRenderData:
	"""Representa un nodo en el formato de render para visualización."""
	id: Any
	label: str
	depth: int
	critical: bool
	final_price: float

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "TreeNodeRenderData":
		return cls(
			id=data.get("id"),
			label=data.get("label", ""),
			depth=data.get("depth", 0),
			critical=data.get("critical", False),
			final_price=data.get("final_price", 0.0),
		)


@dataclass
class TreeEdgeRenderData:
	"""Representa una arista (conexión) entre nodos."""
	from_node: Any
	to_node: Any

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "TreeEdgeRenderData":
		return cls(
			from_node=data.get("from"),
			to_node=data.get("to"),
		)


@dataclass
class TreeRenderData:
	"""Estructura completa de un árbol para renderizar: nodos, aristas y raíz."""
	nodes: list[TreeNodeRenderData]
	edges: list[TreeEdgeRenderData]
	root: Any
	total_nodes: int

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "TreeRenderData":
		nodes = [TreeNodeRenderData.from_dict(n) for n in data.get("nodes", [])]
		edges = [TreeEdgeRenderData.from_dict(e) for e in data.get("edges", [])]
		return cls(
			nodes=nodes,
			edges=edges,
			root=data.get("root"),
			total_nodes=data.get("total_nodes", 0),
		)


@dataclass
class TreeCompareRenderData:
	"""Estructura que contiene datos de render para ambos árboles (AVL y BST)."""
	avl: TreeRenderData
	bst: TreeRenderData

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "TreeCompareRenderData":
		return cls(
			avl=TreeRenderData.from_dict(data.get("avl", {})),
			bst=TreeRenderData.from_dict(data.get("bst", {})),
		)
