from __future__ import annotations

"""
core/bst.py

Implementación de un Árbol Binario de Búsqueda (BST) para el proyecto
SkyBalance AVL.

¿Por qué construir primero el BST?
--------------------------------
Porque el BST nos sirve como base conceptual y funcional para:
1. Reutilizar la lógica de búsqueda y recorridos.
2. Compararlo contra el AVL cuando el JSON se cargue en modo inserción.
3. Tener una estructura de referencia más simple para probar reglas del negocio.

Este archivo está pensado para ser muy didáctico:
- Tiene comentarios amplios.
- Separa helpers internos de métodos públicos.
- Recalcula metadatos del árbol cuando hay cambios.
"""

from collections import deque
from typing import Any, Optional

from models.flight_record import FlightRecord
from models.nodes import TreeNode


class BST:
    """
    Árbol Binario de Búsqueda.

    Regla principal:
    - Todo nodo del subárbol izquierdo tiene clave menor que la del nodo actual.
    - Todo nodo del subárbol derecho tiene clave mayor que la del nodo actual.

    En este proyecto la clave es `flight.code_num`, es decir,
    el código de vuelo normalizado.
    """

    def __init__(self) -> None:
        self.root: Optional[TreeNode] = None
        self._size: int = 0

    # -------------------------------------------------------------------------
    # Propiedades básicas
    # -------------------------------------------------------------------------
    def is_empty(self) -> bool:
        """Retorna True si el árbol no tiene nodos."""
        return self.root is None

    def __len__(self) -> int:
        """Permite usar len(bst)."""
        return self._size

    def size(self) -> int:
        """Devuelve la cantidad de nodos del árbol."""
        return self._size

    # -------------------------------------------------------------------------
    # Inserción
    # -------------------------------------------------------------------------
    def _build_placeholder_flight(self, value: Any) -> FlightRecord:
        """
        Construye un vuelo mínimo a partir de una clave.

        Se usa para compatibilidad con inserciones de estilo académico
        (nodos basados solo en valor).
        """
        return FlightRecord(
            code_raw=value,
            origin="",
            destination="",
            departure_time="",
            base_price=0.0,
            passengers=0,
            priority="MEDIA",
            promotion=0.0,
            alert="NORMAL",
        )

    def _coerce_insert_input(self, value: Any) -> TreeNode:
        """
        Convierte distintos tipos de entrada en un TreeNode válido.

        Entradas soportadas:
        - FlightRecord
        - TreeNode
        - objetos con getValue() (compatibilidad con clase Node del profesor)
        - valores escalares (int/str/float)
        """
        if isinstance(value, TreeNode):
            node = value
        elif isinstance(value, FlightRecord):
            node = TreeNode(flight=value)
        elif hasattr(value, "getValue"):
            node = TreeNode(flight=self._build_placeholder_flight(value.getValue()))
        else:
            node = TreeNode(flight=self._build_placeholder_flight(value))

        # Garantiza inserción limpia como nodo nuevo.
        node.left = None
        node.right = None
        node.parent = None
        return node

    def insert(self, flight: Any) -> TreeNode:
        """
        Inserta un vuelo en el BST.

        Si la clave ya existe, se lanza una excepción.
        En el proyecto esto es útil porque los códigos de vuelo deben ser únicos.

        Parameters
        ----------
        flight : Any
            Puede ser FlightRecord, TreeNode, Node (con getValue) o valor.

        Returns
        -------
        TreeNode
            Nodo creado e insertado.
        """
        new_node = self._coerce_insert_input(flight)

        if self.root is None:
            self.root = new_node
            self._size = 1
            self.refresh_metadata()
            return new_node

        current = self.root
        parent: Optional[TreeNode] = None

        while current is not None:
            parent = current

            if new_node.key < current.key:
                current = current.left
            elif new_node.key > current.key:
                current = current.right
            else:
                raise ValueError(f"Ya existe un vuelo con clave {new_node.key}")

        # parent no puede ser None aquí porque root ya existía.
        new_node.parent = parent
        if new_node.key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._size += 1
        self.refresh_metadata()
        return new_node

    # -------------------------------------------------------------------------
    # Búsqueda
    # -------------------------------------------------------------------------
    def search(self, key: int) -> Optional[TreeNode]:
        """
        Busca un nodo por clave.

        Parameters
        ----------
        key : int
            Clave normalizada del vuelo.

        Returns
        -------
        Optional[TreeNode]
            El nodo si existe; de lo contrario, None.
        """
        current = self.root

        while current is not None:
            if key < current.key:
                current = current.left
            elif key > current.key:
                current = current.right
            else:
                return current

        return None

    def contains(self, key: int) -> bool:
        """Retorna True si la clave existe en el árbol."""
        return self.search(key) is not None

    # -------------------------------------------------------------------------
    # Mínimo, máximo, sucesor
    # -------------------------------------------------------------------------
    def min_node(self, node: Optional[TreeNode] = None) -> Optional[TreeNode]:
        """
        Retorna el nodo de menor clave.

        Si no se pasa un nodo, busca el mínimo del árbol completo.
        """
        current = node if node is not None else self.root
        if current is None:
            return None

        while current.left is not None:
            current = current.left
        return current

    def max_node(self, node: Optional[TreeNode] = None) -> Optional[TreeNode]:
        """
        Retorna el nodo de mayor clave.

        Si no se pasa un nodo, busca el máximo del árbol completo.
        """
        current = node if node is not None else self.root
        if current is None:
            return None

        while current.right is not None:
            current = current.right
        return current

    def successor(self, node: TreeNode) -> Optional[TreeNode]:
        """
        Retorna el sucesor inorder de un nodo.

        El sucesor inorder es el nodo con la menor clave mayor que la actual.
        Es muy útil para la eliminación de nodos con dos hijos.
        """
        if node.right is not None:
            return self.min_node(node.right)

        current = node
        parent = current.parent
        while parent is not None and current == parent.right:
            current = parent
            parent = parent.parent
        return parent

    # -------------------------------------------------------------------------
    # Eliminación
    # -------------------------------------------------------------------------
    def delete(self, key: int) -> bool:
        """
        Elimina un nodo por clave.

        Casos clásicos de eliminación en BST:
        1. Nodo hoja.
        2. Nodo con un solo hijo.
        3. Nodo con dos hijos.

        Returns
        -------
        bool
            True si se eliminó el nodo, False si no existía.
        """
        node = self.search(key)
        if node is None:
            return False

        self._delete_node(node)
        self._size -= 1
        self.refresh_metadata()
        return True

    def _delete_node(self, node: TreeNode) -> None:
        """
        Elimina físicamente un nodo ya localizado.

        Este método es interno. El método público `delete` primero busca
        el nodo y luego llama aquí.
        """
        # Caso 1: el nodo es hoja.
        if node.left is None and node.right is None:
            self._transplant(node, None)
            return

        # Caso 2: solo tiene hijo derecho.
        if node.left is None:
            self._transplant(node, node.right)
            return

        # Caso 2: solo tiene hijo izquierdo.
        if node.right is None:
            self._transplant(node, node.left)
            return

        # Caso 3: tiene dos hijos.
        # Buscamos el sucesor inorder (mínimo del subárbol derecho).
        successor = self.min_node(node.right)
        if successor is None:
            raise RuntimeError("No se encontró sucesor para un nodo con hijo derecho.")

        # Si el sucesor no es el hijo derecho inmediato,
        # hay que reubicar primero el subárbol del sucesor.
        if successor.parent != node:
            self._transplant(successor, successor.right)
            successor.right = node.right
            if successor.right is not None:
                successor.right.parent = successor

        # Ahora reemplazamos el nodo por su sucesor.
        self._transplant(node, successor)
        successor.left = node.left
        if successor.left is not None:
            successor.left.parent = successor

    def _transplant(self, old_node: TreeNode, new_node: Optional[TreeNode]) -> None:
        """
        Reemplaza un subárbol por otro.

        Este helper es la técnica clásica para simplificar la eliminación.

        Parameters
        ----------
        old_node : TreeNode
            Nodo que va a ser reemplazado.
        new_node : Optional[TreeNode]
            Nuevo nodo que tomará su lugar.
        """
        if old_node.parent is None:
            self.root = new_node
        elif old_node == old_node.parent.left:
            old_node.parent.left = new_node
        else:
            old_node.parent.right = new_node

        if new_node is not None:
            new_node.parent = old_node.parent

    # -------------------------------------------------------------------------
    # Cancelación de subárbol
    # -------------------------------------------------------------------------
    def cancel_subtree(self, key: int) -> int:
        """
        Elimina un nodo y toda su descendencia.

        Esta operación es diferente a delete():
        - delete() elimina un solo nodo preservando la estructura BST.
        - cancel_subtree() elimina el nodo completo con todos sus hijos.

        Esto es exactamente lo que pide el proyecto cuando se 'cancela' un vuelo.

        Returns
        -------
        int
            Cantidad de nodos eliminados.
        """
        node = self.search(key)
        if node is None:
            return 0

        removed_count = self._count_subtree_nodes(node)
        self._transplant(node, None)
        self._size -= removed_count
        self.refresh_metadata()
        return removed_count

    def _count_subtree_nodes(self, node: Optional[TreeNode]) -> int:
        """Cuenta cuántos nodos hay en un subárbol."""
        if node is None:
            return 0
        return 1 + self._count_subtree_nodes(node.left) + self._count_subtree_nodes(node.right)

    # -------------------------------------------------------------------------
    # Recorridos
    # -------------------------------------------------------------------------
    def inorder(self) -> list[FlightRecord]:
        """Recorrido inorder: izquierda, raíz, derecha."""
        result: list[FlightRecord] = []

        def _traverse(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            _traverse(node.left)
            result.append(node.flight)
            _traverse(node.right)

        _traverse(self.root)
        return result

    def preorder(self) -> list[FlightRecord]:
        """Recorrido preorder: raíz, izquierda, derecha."""
        result: list[FlightRecord] = []

        def _traverse(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            result.append(node.flight)
            _traverse(node.left)
            _traverse(node.right)

        _traverse(self.root)
        return result

    def postorder(self) -> list[FlightRecord]:
        """Recorrido postorder: izquierda, derecha, raíz."""
        result: list[FlightRecord] = []

        def _traverse(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            _traverse(node.left)
            _traverse(node.right)
            result.append(node.flight)

        _traverse(self.root)
        return result

    def level_order(self) -> list[FlightRecord]:
        """
        Recorrido por niveles (BFS).

        Muy útil para mostrar el árbol en interfaz o depurarlo.
        """
        if self.root is None:
            return []

        result: list[FlightRecord] = []
        queue: deque[TreeNode] = deque([self.root])

        while queue:
            current = queue.popleft()
            result.append(current.flight)

            if current.left is not None:
                queue.append(current.left)
            if current.right is not None:
                queue.append(current.right)

        return result

    # -------------------------------------------------------------------------
    # API de compatibilidad con el estilo del profesor
    # -------------------------------------------------------------------------
    def getRoot(self) -> Optional[TreeNode]:
        return self.root

    def breadthFirstSearch(self) -> list[int]:
        return [flight.code_num for flight in self.level_order()]

    def preOrderTraversal(self) -> list[int]:
        return [flight.code_num for flight in self.preorder()]

    def inOrderTraversal(self) -> list[int]:
        return [flight.code_num for flight in self.inorder()]

    def posOrderTraversal(self) -> list[int]:
        return [flight.code_num for flight in self.postorder()]

    def calculateHeight(self, node: Optional[TreeNode]) -> int:
        """
        Altura con convención del código del profesor:
        - None = -1
        - hoja = 0
        """
        if node is None:
            return -1
        return 1 + max(self.calculateHeight(node.left), self.calculateHeight(node.right))

    # -------------------------------------------------------------------------
    # Métricas estructurales
    # -------------------------------------------------------------------------
    def height(self) -> int:
        """Altura del árbol completo."""
        return self._compute_height(self.root)

    def _compute_height(self, node: Optional[TreeNode]) -> int:
        """
        Calcula la altura de un nodo.

        Convención usada:
        - nodo None -> altura 0
        - hoja -> altura 1
        """
        if node is None:
            return 0
        return 1 + max(self._compute_height(node.left), self._compute_height(node.right))

    def leaf_count(self) -> int:
        """Cuenta cuántas hojas hay en el árbol."""
        return self._leaf_count(self.root)

    def _leaf_count(self, node: Optional[TreeNode]) -> int:
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return 1
        return self._leaf_count(node.left) + self._leaf_count(node.right)

    def depth_of_key(self, key: int) -> Optional[int]:
        """
        Retorna la profundidad de una clave.

        Profundidad de la raíz = 0.
        """
        node = self.search(key)
        if node is None:
            return None
        return node.flight.depth

    def root_key(self) -> Optional[int]:
        """Retorna la clave de la raíz o None si el árbol está vacío."""
        return self.root.key if self.root is not None else None

    # -------------------------------------------------------------------------
    # Actualización de metadatos
    # -------------------------------------------------------------------------
    def refresh_metadata(self, critical_depth_limit: Optional[int] = None) -> None:
        """
        Recalcula profundidad, altura, balance y criticidad para todo el árbol.

        Aunque el BST no se balancea como AVL, sí podemos calcular el
        factor de balance de cada nodo como información diagnóstica.

        Este método es importante porque:
        - el proyecto necesita profundidad y altura actualizadas,
        - la criticidad depende de la profundidad,
        - la exportación JSON debe reflejar el estado real del árbol.
        """

        def _walk(node: Optional[TreeNode], depth: int) -> int:
            if node is None:
                return 0

            left_height = _walk(node.left, depth + 1)
            right_height = _walk(node.right, depth + 1)
            current_height = 1 + max(left_height, right_height)
            balance_factor = left_height - right_height

            node.flight.update_tree_metrics(
                depth=depth,
                height=current_height,
                balance_factor=balance_factor,
            )
            node.flight.update_critical_status(critical_depth_limit)
            return current_height

        _walk(self.root, 0)

    # -------------------------------------------------------------------------
    # Validaciones
    # -------------------------------------------------------------------------
    def validate_bst_property(self) -> bool:
        """
        Verifica que se cumpla la propiedad BST en todo el árbol.

        Esto es útil para depuración y pruebas unitarias.
        """

        def _validate(node: Optional[TreeNode], low: Any, high: Any) -> bool:
            if node is None:
                return True

            if (low is not None and node.key <= low) or (high is not None and node.key >= high):
                return False

            return _validate(node.left, low, node.key) and _validate(node.right, node.key, high)

        return _validate(self.root, None, None)

    # -------------------------------------------------------------------------
    # Exportación y representación
    # -------------------------------------------------------------------------
    def to_topology_dict(self) -> Optional[dict[str, Any]]:
        """
        Exporta el árbol completo en formato jerárquico.

        Si el árbol está vacío, retorna None.
        """
        if self.root is None:
            return None
        return self.root.to_topology_dict()

    def to_insertion_list(self) -> list[dict[str, Any]]:
        """
        Exporta el árbol como una lista de vuelos en recorrido por niveles.

        No reconstruye la misma topología, pero sí sirve como formato tipo
        'lista de inserción' para pruebas o persistencia simple.
        """
        return [flight.to_dict() for flight in self.level_order()]

    def pretty_print(self) -> None:
        """
        Imprime el árbol en consola de forma lateral.

        Útil en desarrollo antes de construir la interfaz Flet.
        """

        def _print(node: Optional[TreeNode], level: int = 0, prefix: str = "R: ") -> None:
            if node is None:
                return

            _print(node.right, level + 1, "D: ")
            print("    " * level + f"{prefix}{node.key} (h={node.flight.height}, bf={node.flight.balance_factor})")
            _print(node.left, level + 1, "I: ")

        _print(self.root)

    # -------------------------------------------------------------------------
    # Construcción auxiliar desde colecciones
    # -------------------------------------------------------------------------
    @classmethod
    def from_flights(cls, flights: list[FlightRecord]) -> "BST":
        """
        Construye un BST insertando una lista de vuelos uno por uno.
        """
        tree = cls()
        for flight in flights:
            tree.insert(flight)
        return tree
