from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from models.flight_record import FlightRecord
from models.normalization import normalize_flight_code


@dataclass
class TreeNode:
    """
    Nodo de arbol para BST y AVL.
    """

    flight: FlightRecord
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None
    parent: Optional["TreeNode"] = None

    @property
    def key(self) -> int:
        return self.flight.code_num

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def has_one_child(self) -> bool:
        return (self.left is None) ^ (self.right is None)

    def child_count(self) -> int:
        return int(self.left is not None) + int(self.right is not None)

    def to_topology_dict(self) -> dict[str, Any]:
        node_data = self.flight.to_dict()
        node_data["izquierdo"] = self.left.to_topology_dict() if self.left else None
        node_data["derecho"] = self.right.to_topology_dict() if self.right else None
        return node_data

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
    Nodo academico ligero para reutilizar codigo de clase.
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
