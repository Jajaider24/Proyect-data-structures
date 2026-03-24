from __future__ import annotations

"""
core/avl.py

Implementación completa de un árbol AVL para el proyecto SkyBalance AVL.

¿Qué agrega este archivo frente al BST?
--------------------------------------
1. Inserción con rebalanceo automático.
2. Eliminación con rebalanceo automático.
3. Rotaciones simples y dobles:
   - LL
   - RR
   - LR
   - RL
4. Modo estrés:
   - permite operar sin balancear inmediatamente.
5. Rebalanceo global:
   - útil cuando se sale del modo estrés.
6. Métricas de rotaciones.
7. Auditoría básica de la propiedad AVL.

IMPORTANTE
----------
Aunque internamente vamos actualizando alturas y balances de forma local,
al final de cada operación se llama `refresh_metadata()` para recalcular:
- profundidad,
- altura,
- factor de equilibrio,
- criticidad por profundidad,
- precio final.

Esto deja el árbol consistente con las reglas del proyecto.
"""

from typing import Any, Optional

from core.bst import BST
from models.flight_record import FlightRecord
from models.nodes import TreeNode


class AVL(BST):
    """
    Árbol AVL.

    Un AVL es un BST auto-balanceado en el que, para cada nodo,
    la diferencia entre la altura del subárbol izquierdo y derecho
    debe permanecer en el rango [-1, 0, 1].

    En este proyecto, la clave de comparación sigue siendo el código
    normalizado del vuelo (`flight.code_num`).
    """

    def __init__(self, critical_depth_limit: Optional[int] = None) -> None:
        super().__init__()

        # Límite opcional para marcar nodos críticos por profundidad.
        self.critical_depth_limit: Optional[int] = critical_depth_limit

        # Cuando stress_mode=True, el árbol permite inserciones/eliminaciones
        # sin rebalancear automáticamente.
        self.stress_mode: bool = False

        # Métricas de rotación por tipo de caso AVL.
        self.rotation_case_counts: dict[str, int] = {
            "LL": 0,
            "RR": 0,
            "LR": 0,
            "RL": 0,
        }

        # Conteo de rotaciones simples ejecutadas realmente.
        # Una rotación doble LR o RL consume dos rotaciones simples.
        self.simple_rotation_counts: dict[str, int] = {
            "left": 0,
            "right": 0,
        }

        # Conteo de cancelaciones masivas.
        self.mass_cancellations: int = 0

    # -------------------------------------------------------------------------
    # Configuración del árbol
    # -------------------------------------------------------------------------
    def set_stress_mode(self, enabled: bool) -> None:
        """
        Activa o desactiva el modo estrés.

        Cuando está activado:
        - el árbol sigue siendo un BST correcto,
        - pero NO se rebalancea después de cada operación.

        Esto reproduce el requisito del proyecto donde el sistema puede
        degradarse temporalmente antes de aplicar un rebalanceo global.
        """
        self.stress_mode = enabled
        self.refresh_metadata()

    def set_critical_depth_limit(self, limit: Optional[int]) -> None:
        """
        Actualiza la profundidad crítica y recalcula todo el árbol.
        """
        self.critical_depth_limit = limit
        self.refresh_metadata()

    def refresh_metadata(self, critical_depth_limit: Optional[int] = None) -> None:
        """
        Recalcula metadatos estructurales y de negocio.

        Si se pasa `critical_depth_limit`, además se actualiza el valor interno.
        """
        if critical_depth_limit is not None:
            self.critical_depth_limit = critical_depth_limit
        super().refresh_metadata(self.critical_depth_limit)

    # -------------------------------------------------------------------------
    # Helpers de altura y balance
    # -------------------------------------------------------------------------
    def _height(self, node: Optional[TreeNode]) -> int:
        """
        Retorna la altura almacenada de un nodo.

        Convención:
        - None -> 0
        - hoja -> 1
        """
        if node is None:
            return 0
        return node.flight.height

    def _balance_factor(self, node: Optional[TreeNode]) -> int:
        """
        Calcula el factor de equilibrio de un nodo.

        factor = altura(izquierda) - altura(derecha)
        """
        if node is None:
            return 0
        return self._height(node.left) - self._height(node.right)

    def _update_node_metrics_local(self, node: Optional[TreeNode]) -> int:
        """
        Recalcula localmente la altura y el balance de un nodo.

        OJO:
        Este método NO actualiza profundidad ni criticidad.
        Es solo para que las rotaciones y el rebalanceo local funcionen.
        La profundidad y la criticidad se recalculan globalmente después.
        """
        if node is None:
            return 0

        left_height = self._height(node.left)
        right_height = self._height(node.right)
        node.flight.height = 1 + max(left_height, right_height)
        node.flight.balance_factor = left_height - right_height
        return node.flight.height

    # -------------------------------------------------------------------------
    # Rotaciones AVL
    # -------------------------------------------------------------------------
    def _rotate_left(self, pivot: TreeNode) -> TreeNode:
        """
        Rotación simple a la izquierda.

        Se usa típicamente para corregir un caso RR.

              pivot                    new_root
                \                       /    \
               new_root    --->      pivot   C
               /    \                /   \
              B      C              A     B
             
        donde A es el hijo izquierdo de pivot.
        """
        new_root = pivot.right
        if new_root is None:
            raise ValueError("No se puede hacer rotación izquierda sin hijo derecho.")

        transferred_subtree = new_root.left

        # 1. Reacomodar el subárbol transferido.
        pivot.right = transferred_subtree
        if transferred_subtree is not None:
            transferred_subtree.parent = pivot

        # 2. Subir new_root y bajar pivot.
        new_root.left = pivot
        parent = pivot.parent
        pivot.parent = new_root
        new_root.parent = parent

        # 3. Enlazar el nuevo subárbol con el abuelo.
        if parent is None:
            self.root = new_root
        elif parent.left == pivot:
            parent.left = new_root
        else:
            parent.right = new_root

        # 4. Actualizar alturas/balances locales de abajo hacia arriba.
        self._update_node_metrics_local(pivot)
        self._update_node_metrics_local(new_root)

        self.simple_rotation_counts["left"] += 1
        return new_root

    def _rotate_right(self, pivot: TreeNode) -> TreeNode:
        """
        Rotación simple a la derecha.

        Se usa típicamente para corregir un caso LL.

                pivot                 new_root
                /                       /    \
           new_root      --->          A    pivot
            /    \                          /   \
           A      B                        B     C
        """
        new_root = pivot.left
        if new_root is None:
            raise ValueError("No se puede hacer rotación derecha sin hijo izquierdo.")

        transferred_subtree = new_root.right

        # 1. Reacomodar el subárbol transferido.
        pivot.left = transferred_subtree
        if transferred_subtree is not None:
            transferred_subtree.parent = pivot

        # 2. Subir new_root y bajar pivot.
        new_root.right = pivot
        parent = pivot.parent
        pivot.parent = new_root
        new_root.parent = parent

        # 3. Enlazar el nuevo subárbol con el abuelo.
        if parent is None:
            self.root = new_root
        elif parent.left == pivot:
            parent.left = new_root
        else:
            parent.right = new_root

        # 4. Actualizar alturas/balances locales.
        self._update_node_metrics_local(pivot)
        self._update_node_metrics_local(new_root)

        self.simple_rotation_counts["right"] += 1
        return new_root

    # -------------------------------------------------------------------------
    # Lógica central de rebalanceo
    # -------------------------------------------------------------------------
    def _rebalance_at(self, node: TreeNode) -> TreeNode:
        """
        Rebalancea un nodo concreto si está desbalanceado.

        Casos cubiertos:
        - LL: rotación derecha
        - RR: rotación izquierda
        - LR: izquierda sobre hijo izquierdo y luego derecha
        - RL: derecha sobre hijo derecho y luego izquierda

        Returns
        -------
        TreeNode
            Nueva raíz del subárbol rebalanceado.
        """
        # Aseguramos que hijos y nodo actual tengan alturas recientes.
        self._update_node_metrics_local(node.left)
        self._update_node_metrics_local(node.right)
        self._update_node_metrics_local(node)

        bf = self._balance_factor(node)

        # Caso pesado a la izquierda.
        if bf > 1:
            left_bf = self._balance_factor(node.left)

            # Caso LL -> rotación simple a la derecha.
            if left_bf >= 0:
                self.rotation_case_counts["LL"] += 1
                return self._rotate_right(node)

            # Caso LR -> izquierda en hijo izquierdo + derecha en nodo.
            self.rotation_case_counts["LR"] += 1
            if node.left is None:
                raise RuntimeError("Caso LR inválido: el nodo no tiene hijo izquierdo.")
            self._rotate_left(node.left)
            return self._rotate_right(node)

        # Caso pesado a la derecha.
        if bf < -1:
            right_bf = self._balance_factor(node.right)

            # Caso RR -> rotación simple a la izquierda.
            if right_bf <= 0:
                self.rotation_case_counts["RR"] += 1
                return self._rotate_left(node)

            # Caso RL -> derecha en hijo derecho + izquierda en nodo.
            self.rotation_case_counts["RL"] += 1
            if node.right is None:
                raise RuntimeError("Caso RL inválido: el nodo no tiene hijo derecho.")
            self._rotate_right(node.right)
            return self._rotate_left(node)

        # Si no estaba desbalanceado, regresa igual.
        return node

    def _rebalance_upward_from(self, start_node: Optional[TreeNode]) -> None:
        """
        Rebalancea desde un nodo hacia arriba hasta llegar a la raíz.

        Esta es la rutina típica usada después de inserciones o eliminaciones.
        """
        current = start_node

        while current is not None:
            # Recalcular localmente el nodo actual.
            self._update_node_metrics_local(current)

            # Si está desbalanceado, se corrige.
            current = self._rebalance_at(current)

            # Seguimos hacia el padre de la nueva raíz local.
            current = current.parent

    # -------------------------------------------------------------------------
    # Inserción
    # -------------------------------------------------------------------------
    def insert(self, flight: Any) -> TreeNode:
        """
        Inserta un vuelo en el AVL.

        Si el árbol está en modo normal:
        - inserta como un BST,
        - rebalancea desde el padre del nuevo nodo hacia arriba.

        Si está en modo estrés:
        - inserta como un BST,
        - NO rebalancea.
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

        new_node.parent = parent
        if new_node.key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._size += 1

        if not self.stress_mode:
            self._rebalance_upward_from(parent)

        self.refresh_metadata()
        return new_node

    # -------------------------------------------------------------------------
    # Eliminación
    # -------------------------------------------------------------------------
    def delete(self, key: int) -> bool:
        """
        Elimina un nodo por clave.

        En modo normal, después de la eliminación aplica rebalanceo AVL.
        En modo estrés, solo modifica la estructura BST y recalcula métricas.
        """
        node = self.search(key)
        if node is None:
            return False

        rebalance_points: list[Optional[TreeNode]] = []

        # Caso 1 y 2: nodo con 0 o 1 hijo.
        if node.left is None:
            replacement = node.right
            rebalance_points.append(node.parent if node.parent is not None else replacement)
            self._transplant(node, replacement)

        elif node.right is None:
            replacement = node.left
            rebalance_points.append(node.parent if node.parent is not None else replacement)
            self._transplant(node, replacement)

        # Caso 3: nodo con dos hijos.
        else:
            successor = self.min_node(node.right)
            if successor is None:
                raise RuntimeError("No se encontró sucesor al eliminar un nodo con dos hijos.")

            old_successor_parent = successor.parent

            # Si el sucesor no es el hijo derecho inmediato,
            # primero lo removemos de su sitio original.
            if successor.parent != node:
                self._transplant(successor, successor.right)
                successor.right = node.right
                if successor.right is not None:
                    successor.right.parent = successor
                rebalance_points.append(old_successor_parent)

            # Ahora el sucesor reemplaza al nodo eliminado.
            self._transplant(node, successor)
            successor.left = node.left
            if successor.left is not None:
                successor.left.parent = successor

            rebalance_points.append(successor)

        self._size -= 1

        if not self.stress_mode:
            for start in rebalance_points:
                self._rebalance_upward_from(start)

        self.refresh_metadata()
        return True

    # -------------------------------------------------------------------------
    # Cancelación de subárbol
    # -------------------------------------------------------------------------
    def cancel_subtree(self, key: int) -> int:
        """
        Elimina un nodo con toda su descendencia.

        Diferencia frente a delete():
        - delete() conserva el resto del árbol y solo elimina un nodo.
        - cancel_subtree() elimina la subrama completa.

        Esta operación coincide con el requisito de 'cancelar vuelo' del proyecto.
        """
        node = self.search(key)
        if node is None:
            return 0

        removed_count = self._count_subtree_nodes(node)
        parent = node.parent
        self._transplant(node, None)
        self._size -= removed_count
        self.mass_cancellations += 1

        if not self.stress_mode:
            self._rebalance_upward_from(parent)

        self.refresh_metadata()
        return removed_count

    # -------------------------------------------------------------------------
    # Rebalanceo global
    # -------------------------------------------------------------------------
    def _postorder_nodes(self, node: Optional[TreeNode]) -> list[TreeNode]:
        """
        Retorna una lista de nodos en postorden.

        El postorden es útil para intentar reequilibrar primero los niveles
        más profundos y luego subir hacia la raíz.
        """
        if node is None:
            return []
        return self._postorder_nodes(node.left) + self._postorder_nodes(node.right) + [node]

    def rebalance_global(self) -> dict[str, int]:
        """
        Intenta restaurar la propiedad AVL sobre todo el árbol.

        Pensado para usarse al salir del modo estrés.

        Estrategia:
        - recorre nodos en postorden,
        - detecta desbalances,
        - aplica rotaciones en cascada,
        - repite hasta que no haya cambios.

        Returns
        -------
        dict[str, int]
            Resumen del costo estructural del rebalanceo global.
        """
        before_cases = self.rotation_case_counts.copy()
        before_simple = self.simple_rotation_counts.copy()

        if self.root is None:
            self.stress_mode = False
            return {
                "LL": 0,
                "RR": 0,
                "LR": 0,
                "RL": 0,
                "simple_left": 0,
                "simple_right": 0,
            }

        # Evitamos loops infinitos con un límite generoso.
        max_iterations = max(10, self.size() * 5)
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            changed = False

            # Tomamos una fotografía en postorden del estado actual.
            nodes = self._postorder_nodes(self.root)
            for node in nodes:
                # El nodo puede seguir existiendo, pero su posición pudo cambiar.
                # Igual sigue siendo válido como referencia del objeto.
                old_root_key = self.root.key if self.root is not None else None
                old_node_parent = node.parent
                old_node_key = node.key

                self._update_node_metrics_local(node.left)
                self._update_node_metrics_local(node.right)
                self._update_node_metrics_local(node)

                if abs(self._balance_factor(node)) > 1:
                    self._rebalance_at(node)
                    changed = True

                # Esta comparación no es perfecta, pero ayuda a capturar cambios.
                if self.root is not None and self.root.key != old_root_key:
                    changed = True
                if node.parent != old_node_parent:
                    changed = True
                if node.key != old_node_key:
                    changed = True

            self.refresh_metadata()

            # Si ya no hubo cambios, el árbol quedó estable.
            if not changed:
                break

        self.stress_mode = False
        self.refresh_metadata()

        return {
            "LL": self.rotation_case_counts["LL"] - before_cases["LL"],
            "RR": self.rotation_case_counts["RR"] - before_cases["RR"],
            "LR": self.rotation_case_counts["LR"] - before_cases["LR"],
            "RL": self.rotation_case_counts["RL"] - before_cases["RL"],
            "simple_left": self.simple_rotation_counts["left"] - before_simple["left"],
            "simple_right": self.simple_rotation_counts["right"] - before_simple["right"],
        }

    # -------------------------------------------------------------------------
    # Métricas y reportes
    # -------------------------------------------------------------------------
    def rotation_summary(self) -> dict[str, int]:
        """
        Retorna un resumen completo de las rotaciones acumuladas.
        """
        return {
            **self.rotation_case_counts,
            "simple_left": self.simple_rotation_counts["left"],
            "simple_right": self.simple_rotation_counts["right"],
            "simple_total": self.simple_rotation_counts["left"] + self.simple_rotation_counts["right"],
            "mass_cancellations": self.mass_cancellations,
        }

    def total_rotations(self) -> int:
        """
        Retorna el total de rotaciones simples ejecutadas.
        """
        return self.simple_rotation_counts["left"] + self.simple_rotation_counts["right"]

    # -------------------------------------------------------------------------
    # Auditoría básica de la propiedad AVL
    # -------------------------------------------------------------------------
    def audit_avl(self) -> dict[str, Any]:
        """
        Recorre el árbol y verifica si cumple la propiedad AVL.

        Este método es muy útil para el punto del proyecto donde se exige
        'Verificar Propiedad AVL' y reportar inconsistencias.

        Returns
        -------
        dict[str, Any]
            Reporte con validez general, errores y nodos conflictivos.
        """
        issues: list[str] = []
        unbalanced_nodes: list[int] = []
        invalid_height_nodes: list[int] = []

        def _audit(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0

            left_height = _audit(node.left)
            right_height = _audit(node.right)
            computed_height = 1 + max(left_height, right_height)
            computed_bf = left_height - right_height

            if abs(computed_bf) > 1:
                unbalanced_nodes.append(node.key)
                issues.append(
                    f"Nodo {node.key} desbalanceado: factor calculado = {computed_bf}."
                )

            if node.flight.height != computed_height:
                invalid_height_nodes.append(node.key)
                issues.append(
                    f"Nodo {node.key} con altura inconsistente: almacenada = {node.flight.height}, calculada = {computed_height}."
                )

            if node.flight.balance_factor != computed_bf:
                issues.append(
                    f"Nodo {node.key} con balance inconsistente: almacenado = {node.flight.balance_factor}, calculado = {computed_bf}."
                )

            return computed_height

        overall_height = _audit(self.root)
        bst_ok = self.validate_bst_property()

        if not bst_ok:
            issues.append("La propiedad BST no se cumple en todo el árbol.")

        is_valid = bst_ok and len(unbalanced_nodes) == 0 and len(invalid_height_nodes) == 0

        return {
            "is_valid_avl": is_valid,
            "bst_property_ok": bst_ok,
            "tree_height": overall_height,
            "node_count": self.size(),
            "unbalanced_nodes": unbalanced_nodes,
            "invalid_height_nodes": invalid_height_nodes,
            "issues": issues,
        }

    # -------------------------------------------------------------------------
    # API de compatibilidad con el estilo del profesor
    # -------------------------------------------------------------------------
    def getBalanceFactor(self, node: Optional[TreeNode]) -> int:
        if node is None:
            return 0
        return self._balance_factor(node)

    def print_tree(self) -> None:
        self.pretty_print()

    # -------------------------------------------------------------------------
    # Construcción auxiliar
    # -------------------------------------------------------------------------
    @classmethod
    def from_flights(cls, flights: list[FlightRecord], critical_depth_limit: Optional[int] = None) -> "AVL":
        """
        Construye un AVL insertando una lista de vuelos uno por uno.
        """
        tree = cls(critical_depth_limit=critical_depth_limit)
        for flight in flights:
            tree.insert(flight)
        return tree
