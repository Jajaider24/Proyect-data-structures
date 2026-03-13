from __future__ import annotations

"""
core/models.py

Modelos base del proyecto SkyBalance AVL.

Este archivo define:
1. La estructura de datos del vuelo (FlightRecord).
2. La estructura del nodo del árbol (TreeNode).
3. Utilidades para normalizar códigos de vuelo.
4. Reglas básicas de negocio relacionadas con precio final,
   profundidad crítica y serialización.

La idea es que TODO el proyecto use estas clases como base común.
Así evitamos mezclar lógica del árbol con datos del negocio.
"""

from dataclasses import dataclass, field
from typing import Any, Optional
import re


# -----------------------------------------------------------------------------
# Utilidades de normalización
# -----------------------------------------------------------------------------

def normalize_flight_code(code: Any) -> int:
    """
    Convierte distintos formatos de código de vuelo en una clave numérica.

    Ejemplos:
    - "SB400" -> 400
    - "AVL-275" -> 275
    - 500 -> 500
    - "500" -> 500

    Esta función es clave para el proyecto porque los JSON del profesor
    no usan siempre el mismo formato de código.
    El árbol NO debe comparar strings como "SB400" directamente,
    sino la parte numérica normalizada.

    Parameters
    ----------
    code : Any
        Código original del vuelo.

    Returns
    -------
    int
        Parte numérica del código.

    Raises
    ------
    ValueError
        Si no se puede extraer una parte numérica válida.
    """
    if isinstance(code, int):
        return code

    if isinstance(code, float):
        # Solo aceptamos float si representa un entero exacto.
        if code.is_integer():
            return int(code)
        raise ValueError(f"El código numérico no es entero: {code}")

    code_str = str(code).strip()
    digits = re.findall(r"\d+", code_str)

    if not digits:
        raise ValueError(f"No se pudo normalizar el código de vuelo: {code}")

    return int("".join(digits))


# -----------------------------------------------------------------------------
# Modelo de negocio del vuelo
# -----------------------------------------------------------------------------

@dataclass
class FlightRecord:
    """
    Representa toda la información de negocio asociada a un vuelo.

    Importante:
    - code_raw conserva el valor tal como llegó del usuario o del JSON.
    - code_num es la clave real con la que se ordenará el árbol.
    - final_price se recalcula cuando cambian reglas del sistema.
    - depth, height y balance_factor se actualizan desde el árbol.
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

    # Campos calculados / derivados
    code_num: int = field(init=False)
    final_price: float = 0.0
    is_critical: bool = False
    depth: int = 0
    height: int = 1
    balance_factor: int = 0
    critical_penalty_rate: float = 0.25

    def __post_init__(self) -> None:
        """
        Inicializa campos derivados después de crear la instancia.
        """
        self.code_num = normalize_flight_code(self.code_raw)
        self.base_price = float(self.base_price)
        self.promotion = float(self.promotion)
        self.passengers = int(self.passengers)
        self.final_price = round(self.base_price, 2)

    # -----------------------------------------------------------------
    # Reglas del negocio
    # -----------------------------------------------------------------
    def update_critical_status(self, critical_depth_limit: Optional[int]) -> None:
        """
        Marca el vuelo como crítico si supera la profundidad límite.

        Regla del proyecto:
        - Si un nodo supera la profundidad crítica definida por el usuario,
          se marca como crítico y su precio debe incrementarse.

        Parameters
        ----------
        critical_depth_limit : Optional[int]
            Profundidad máxima permitida. Si es None, no aplica la regla.
        """
        if critical_depth_limit is None:
            self.is_critical = False
            self.recalculate_final_price()
            return

        self.is_critical = self.depth > critical_depth_limit
        self.recalculate_final_price()

    def recalculate_final_price(self) -> None:
        """
        Recalcula el precio final del vuelo.

        Regla implementada por ahora:
        - base_price
        - menos promoción
        - más recargo por criticidad si aplica

        Nota:
        En el proyecto la promoción y la penalización pueden reportarse
        también por separado. Aquí dejamos la base lista para eso.
        """
        price = self.base_price - self.promotion

        if self.is_critical:
            price += self.base_price * self.critical_penalty_rate

        # Evitar precios negativos por promociones muy grandes.
        self.final_price = round(max(price, 0.0), 2)

    def economic_profitability(self) -> float:
        """
        Calcula una métrica de rentabilidad para el vuelo.

        Fórmula base del proyecto:
            pasajeros × precioFinal – promoción + penalización

        Aquí modelamos la penalización crítica como el recargo que ya está
        incorporado en el precio final. Para trazabilidad también calculamos
        el valor monetario explícito del recargo.
        """
        critical_penalty_value = 0.0
        if self.is_critical:
            critical_penalty_value = self.base_price * self.critical_penalty_rate

        return (self.passengers * self.final_price) - self.promotion + critical_penalty_value

    # -----------------------------------------------------------------
    # Métodos auxiliares
    # -----------------------------------------------------------------
    def update_tree_metrics(self, depth: int, height: int, balance_factor: int) -> None:
        """
        Actualiza los metadatos estructurales del vuelo.

        Esto lo llamará el árbol después de inserciones, eliminaciones,
        rebalanceos o auditorías.
        """
        self.depth = depth
        self.height = height
        self.balance_factor = balance_factor

    def to_dict(self) -> dict[str, Any]:
        """
        Convierte el vuelo a diccionario serializable.
        """
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
        """
        Crea un FlightRecord a partir de un diccionario.

        Soporta tanto los JSON de inserción como los de topología,
        aunque no todos traen exactamente los mismos campos.
        """
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

        # Si el JSON ya trae algunos datos calculados, se cargan.
        # Sin embargo, el proyecto debe RECALCULAR internamente después.
        record.final_price = float(data.get("precioFinal", record.final_price))
        record.is_critical = bool(data.get("esCritico", record.is_critical))
        record.depth = int(data.get("profundidad", record.depth))
        record.height = int(data.get("altura", record.height))
        record.balance_factor = int(data.get("factorEquilibrio", record.balance_factor))
        return record


# -----------------------------------------------------------------------------
# Nodo del árbol
# -----------------------------------------------------------------------------

@dataclass
class TreeNode:
    """
    Nodo genérico para BST y AVL.

    Contiene una referencia al vuelo y enlaces a hijos / padre.
    La lógica de rebalanceo y recorridos NO debe ir aquí,
    sino en las clases del árbol.
    """

    flight: FlightRecord
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None
    parent: Optional["TreeNode"] = None

    @property
    def key(self) -> int:
        """
        Clave numérica con la que el árbol ordena el nodo.
        """
        return self.flight.code_num

    def is_leaf(self) -> bool:
        """
        Retorna True si el nodo no tiene hijos.
        """
        return self.left is None and self.right is None

    def has_one_child(self) -> bool:
        """
        Retorna True si el nodo tiene exactamente un hijo.
        """
        return (self.left is None) ^ (self.right is None)

    def child_count(self) -> int:
        """
        Cantidad de hijos del nodo.
        """
        return int(self.left is not None) + int(self.right is not None)

    def to_topology_dict(self) -> dict[str, Any]:
        """
        Serializa el nodo y su subárbol en formato jerárquico.

        Este método será útil para exportar el árbol completo a JSON.
        """
        node_data = self.flight.to_dict()
        node_data["izquierdo"] = self.left.to_topology_dict() if self.left else None
        node_data["derecho"] = self.right.to_topology_dict() if self.right else None
        return node_data

    # -----------------------------------------------------------------
    # API de compatibilidad con el estilo del profesor
    # -----------------------------------------------------------------
    def setParent(self, parentNode: Optional["TreeNode"]) -> None:
        self.parent = parentNode

    def getParent(self) -> Optional["TreeNode"]:
        return self.parent

    def setLeftChild(self, leftChildNode: Optional["TreeNode"]) -> None:
        self.left = leftChildNode

    def getLeftChild(self) -> Optional["TreeNode"]:
        return self.left

    def setRightChild(self, rightChildNode: Optional["TreeNode"]) -> None:
        self.right = rightChildNode

    def getRightChild(self) -> Optional["TreeNode"]:
        return self.right

    def getValue(self) -> int:
        return self.key

    def setValue(self, value: Any) -> None:
        normalized = normalize_flight_code(value)
        self.flight.code_raw = value
        self.flight.code_num = normalized


class Node:
    """
    Nodo ligero de compatibilidad con el formato del profesor.

    Este nodo no reemplaza a TreeNode en el proyecto; se usa como
    adaptador cuando se quiere reutilizar código académico basado en
    valores enteros y API con getters/setters.
    """

    def __init__(self, value: Any):
        self.value = normalize_flight_code(value)
        self.parent: Optional["Node"] = None
        self.leftChild: Optional["Node"] = None
        self.rightChild: Optional["Node"] = None

    def setParent(self, parentNode: Optional["Node"]) -> None:
        self.parent = parentNode

    def getParent(self) -> Optional["Node"]:
        return self.parent

    def setLeftChild(self, leftChildNode: Optional["Node"]) -> None:
        self.leftChild = leftChildNode

    def getLeftChild(self) -> Optional["Node"]:
        return self.leftChild

    def setRightChild(self, rightChildNode: Optional["Node"]) -> None:
        self.rightChild = rightChildNode

    def getRightChild(self) -> Optional["Node"]:
        return self.rightChild

    def getValue(self) -> int:
        return self.value

    def setValue(self, value: Any) -> None:
        self.value = normalize_flight_code(value)
