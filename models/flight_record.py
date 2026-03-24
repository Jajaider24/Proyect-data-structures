from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

from models.normalization import normalize_flight_code


@dataclass
class FlightRecord:
    """
    Representa toda la informacion de negocio asociada a un vuelo.
    """

    code_raw: Any
    origin: str
    destination: str
    departure_time: str
    base_price: float
    passengers: int
    priority: str = "MEDIA"
    promotion: float = 0.0
    alert: str = "NORMAL"

    code_num: int = field(init=False)
    final_price: float = 0.0
    is_critical: bool = False
    depth: int = 0
    height: int = 1
    balance_factor: int = 0
    critical_penalty_rate: float = 0.25

    def __post_init__(self) -> None:
        self.code_num = normalize_flight_code(self.code_raw)
        self.base_price = float(self.base_price)
        self.promotion = float(self.promotion)
        self.passengers = int(self.passengers)
        self.final_price = round(self.base_price, 2)

    def update_critical_status(self, critical_depth_limit: Optional[int]) -> None:
        if critical_depth_limit is None:
            self.is_critical = False
            self.recalculate_final_price()
            return

        self.is_critical = self.depth > critical_depth_limit
        self.recalculate_final_price()

    def recalculate_final_price(self) -> None:
        price = self.base_price - self.promotion
        if self.is_critical:
            price += self.base_price * self.critical_penalty_rate
        self.final_price = round(max(price, 0.0), 2)

    def economic_profitability(self) -> float:
        critical_penalty_value = 0.0
        if self.is_critical:
            critical_penalty_value = self.base_price * self.critical_penalty_rate

        return (self.passengers * self.final_price) - self.promotion + critical_penalty_value

    def update_tree_metrics(self, depth: int, height: int, balance_factor: int) -> None:
        self.depth = depth
        self.height = height
        self.balance_factor = balance_factor

    def to_dict(self) -> dict[str, Any]:
        return {
            "codigo": self.code_raw,
            "codigoNormalizado": self.code_num,
            "origen": self.origin,
            "destino": self.destination,
            "horaSalida": self.departure_time,
            "precioBase": self.base_price,
            "precioFinal": self.final_price,
            "pasajeros": self.passengers,
            "prioridad": self.priority,
            "promocion": self.promotion,
            "alerta": self.alert,
            "esCritico": self.is_critical,
            "profundidad": self.depth,
            "altura": self.height,
            "factorEquilibrio": self.balance_factor,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FlightRecord":
        record = cls(
            code_raw=data.get("codigo"),
            origin=data.get("origen", ""),
            destination=data.get("destino", ""),
            departure_time=data.get("horaSalida", ""),
            base_price=data.get("precioBase", 0.0),
            passengers=data.get("pasajeros", 0),
            priority=data.get("prioridad", "MEDIA"),
            promotion=data.get("promocion", 0.0),
            alert=data.get("alerta", "NORMAL"),
        )

        record.final_price = float(data.get("precioFinal", record.final_price))
        record.is_critical = bool(data.get("esCritico", record.is_critical))
        record.depth = int(data.get("profundidad", record.depth))
        record.height = int(data.get("altura", record.height))
        record.balance_factor = int(data.get("factorEquilibrio", record.balance_factor))
        return record
