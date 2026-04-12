from __future__ import annotations

from typing import Any

from core.bst import BST
from models.flight_record import FlightRecord


def _profitability(flight: FlightRecord) -> float:
    return float(flight.economic_profitability())


def calculate_tree_economics(tree: BST) -> dict[str, Any]:
    flights = tree.inorder()
    if not flights:
        return {
            "flight_count": 0,
            "total_passengers": 0,
            "base_revenue": 0.0,
            "final_revenue": 0.0,
            "total_profitability": 0.0,
            "critical_flights": 0,
            "avg_final_price": 0.0,
        }

    total_passengers = sum(flight.passengers for flight in flights)
    base_revenue = sum(flight.base_price * flight.passengers for flight in flights)
    final_revenue = sum(flight.final_price * flight.passengers for flight in flights)
    total_profitability = sum(_profitability(flight) for flight in flights)
    critical_flights = sum(1 for flight in flights if flight.is_critical)
    avg_final_price = sum(flight.final_price for flight in flights) / len(flights)

    return {
        "flight_count": len(flights),
        "total_passengers": total_passengers,
        "base_revenue": round(base_revenue, 2),
        "final_revenue": round(final_revenue, 2),
        "total_profitability": round(total_profitability, 2),
        "critical_flights": critical_flights,
        "avg_final_price": round(avg_final_price, 2),
    }


def top_profitable_flights(tree: BST, limit: int = 5) -> list[dict[str, Any]]:
    flights = sorted(tree.inorder(), key=_profitability, reverse=True)

    result: list[dict[str, Any]] = []
    for flight in flights[: max(limit, 0)]:
        result.append(
            {
                "codigo": flight.code_raw,
                "codigoNormalizado": flight.code_num,
                "origen": flight.origin,
                "destino": flight.destination,
                "pasajeros": flight.passengers,
                "precioFinal": flight.final_price,
                "rentabilidad": round(_profitability(flight), 2),
            }
        )
    return result


def least_profitable_flight(tree: BST) -> dict[str, Any] | None:
    """
    Return the least profitable flight by applying the project's tie-breaking criteria:
    1) lowest profitability,
    2) greatest depth,
    3) highest normalized code.
    """
    flights = tree.inorder()
    if not flights:
        return None

    selected = min(
        flights,
        key=lambda flight: (
            _profitability(flight),
            -int(flight.depth),
            -int(flight.code_num),
        ),
    )

    return {
        "codigo": selected.code_raw,
        "codigoNormalizado": selected.code_num,
        "origen": selected.origin,
        "destino": selected.destination,
        "pasajeros": selected.passengers,
        "precioFinal": selected.final_price,
        "profundidad": selected.depth,
        "rentabilidad": round(_profitability(selected), 2),
    }


def recalculate_prices(tree: BST, critical_depth_limit: int | None = None) -> None:
    tree.refresh_metadata(critical_depth_limit)
