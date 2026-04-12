from __future__ import annotations

"""
core/avl.py

Complete implementation of an AVL tree for the SkyBalance AVL project.

What does this file offer over the BST?
--------------------------------------
1. Insertion with automatic rebalancing.
2. Deletion with automatic rebalancing.
3. Single and double rotations:
   - LL
   - RR
   - LR
   - RL
4. Stress mode:
   - allows operation without immediate rebalancing.
5. Global rebalancing:
   - useful when exiting stress mode.
6. Rotation metrics.
7. Basic audit of the AVL property.

IMPORTANT
----------
Although we internally update heights and balances locally,
at the end of each operation, `refresh_metadata()` is called to recalculate:
- depth,
- height,
- balance factor,
- criticality by depth,
- final price.

This ensures the tree remains consistent with the project rules.
"""

from typing import Any, Optional

from core.bst import BST
from models.flight_record import FlightRecord
from models.nodes import TreeNode


class AVL(BST):
    """
    AVL Tree.

    An AVL tree is a self-balancing BST in which, for each node,
    the difference between the heights of the left and right subtrees
    must remain within the range [-1, 0, 1].

    In this project, the comparison key remains the
    normalized flight code (`flight.code_num`).
    """

    def __init__(self, critical_depth_limit: Optional[int] = None) -> None:
        super().__init__()

        # Optional limit for marking critical nodes by depth.
        self.critical_depth_limit: Optional[int] = critical_depth_limit

        # When stress_mode=True, the tree allows insertions/deletions
        # without automatically rebalancing.
        self.stress_mode: bool = False

        # Rotation metrics by AVL case type.
        self.rotation_case_counts: dict[str, int] = {
            "LL": 0,
            "RR": 0,
            "LR": 0,
            "RL": 0,
        }

        # Count of simple rotations executed.
        # A double rotation (LR or RL) consumes two simple rotations.
        self.simple_rotation_counts: dict[str, int] = {
            "left": 0,
            "right": 0,
        }

        # Count of mass cancellations.
        self.mass_cancellations: int = 0

    # -------------------------------------------------------------------------
    # Tree Configuration
    # -------------------------------------------------------------------------
    def set_stress_mode(self, enabled: bool) -> None:
        """
        Enable or disable stress mode.

        When enabled:
        - the tree remains a valid BST,
        - but it is NOT rebalanced after each operation.

        This replicates the project requirement where the system may
        temporarily degrade before a global rebalance is performed.
        """
        self.stress_mode = enabled
        self.refresh_metadata()

    def set_critical_depth_limit(self, limit: Optional[int]) -> None:
        """
        Updates the critical depth limit and recalculates the entire tree.
        """
        self.critical_depth_limit = limit
        self.refresh_metadata()

    def refresh_metadata(self, critical_depth_limit: Optional[int] = None) -> None:
        """
        Recalculate structural and business metadata.

        If `critical_depth_limit` is passed, the internal value is also updated.
        """
        if critical_depth_limit is not None:
            self.critical_depth_limit = critical_depth_limit
        super().refresh_metadata(self.critical_depth_limit)

    # -------------------------------------------------------------------------
    # Height and balance aids
    # -------------------------------------------------------------------------
    def _height(self, node: Optional[TreeNode]) -> int:
        """
        Returns the stored height of a node.

        Convention:
        - None -> -1
        - leaf -> 0
        """
        if node is None:
            return -1
        return node.flight.height

    def _balance_factor(self, node: Optional[TreeNode]) -> int:
        """
        Calculate the balance factor of a node.

        factor = height(left) - height(right)
        """
        if node is None:
            return 0
        return self._height(node.left) - self._height(node.right)

    def _update_node_metrics_local(self, node: Optional[TreeNode]) -> int:
        """
        Recalculates the height and balance of a node locally.

        NOTE:
        This method does NOT update depth or criticality.
        It is only intended to ensure that rotations and local rebalancing work properly.
        Depth and criticality are recalculated globally afterward.
        """
        if node is None:
            return -1

        left_height = self._height(node.left)
        right_height = self._height(node.right)
        node.flight.height = 1 + max(left_height, right_height)
        node.flight.balance_factor = left_height - right_height
        return node.flight.height

    # -------------------------------------------------------------------------
    # Rotations AVL
    # -------------------------------------------------------------------------
    def _rotate_left(self, pivot: TreeNode) -> TreeNode:
        """
        Simple left rotation.

        It is typically used to correct a right-right (RR) case.

              pivot                    new_root
                \                       /    \
               new_root    --->      pivot   C
               /    \                /   \
              B      C              A     B
             
        where A is the left child of pivot.
        """
        new_root = pivot.right
        if new_root is None:
            raise ValueError("No se puede hacer rotación izquierda sin hijo derecho.")

        transferred_subtree = new_root.left

        # 1. Rearrange the transferred subtree.
        pivot.right = transferred_subtree
        if transferred_subtree is not None:
            transferred_subtree.parent = pivot

        # 2. Lift new_root and lower pivot.
        new_root.left = pivot
        parent = pivot.parent
        pivot.parent = new_root
        new_root.parent = parent

        # 3. Link the new subtree to the grandparent.
        if parent is None:
            self.root = new_root
        elif parent.left == pivot:
            parent.left = new_root
        else:
            parent.right = new_root

        # 4. Update heights/balances locally from bottom to top.
        self._update_node_metrics_local(pivot)
        self._update_node_metrics_local(new_root)

        self.simple_rotation_counts["left"] += 1
        return new_root

    def _rotate_right(self, pivot: TreeNode) -> TreeNode:
        """
        Simple right rotation.

        It is typically used to correct a left-left (LL) case.

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

        # 1. Reorganize the transferred subtree.
        pivot.left = transferred_subtree
        if transferred_subtree is not None:
            transferred_subtree.parent = pivot

        # 2. Lift new_root and lower pivot.
        new_root.right = pivot
        parent = pivot.parent
        pivot.parent = new_root
        new_root.parent = parent

        # 3. Link the new subtree to the grandparent.
        if parent is None:
            self.root = new_root
        elif parent.left == pivot:
            parent.left = new_root
        else:
            parent.right = new_root

        # 4. Update heights/balances locally.
        self._update_node_metrics_local(pivot)
        self._update_node_metrics_local(new_root)

        self.simple_rotation_counts["right"] += 1
        return new_root

    # -------------------------------------------------------------------------
    # Core rebalancing logic
    # -------------------------------------------------------------------------
    def _rebalance_at(self, node: TreeNode) -> TreeNode:
        """
        Rebalance a specific node if it is unbalanced.

        Cases covered:
        - LL: right rotation
        - RR: left rotation
        - LR: left rotation on the left child, followed by right rotation
        - RL: right rotation on the right child, followed by left rotation

        Returns
        -------
        TreeNode
            New root of the rebalanced subtree.
        """
        # We ensure that children and the current node have up-to-date heights.
        self._update_node_metrics_local(node.left)
        self._update_node_metrics_local(node.right)
        self._update_node_metrics_local(node)

        bf = self._balance_factor(node)

        # Case heavy on the left.
        if bf > 1:
            left_bf = self._balance_factor(node.left)

            # Case LL -> simple right rotation.
            if left_bf >= 0:
                self.rotation_case_counts["LL"] += 1
                return self._rotate_right(node)

            # Case LR -> left rotation on the left child, followed by right rotation.
            self.rotation_case_counts["LR"] += 1
            if node.left is None:
                raise RuntimeError("Caso LR inválido: el nodo no tiene hijo izquierdo.")
            self._rotate_left(node.left)
            return self._rotate_right(node)

        # Heavy on the right.
        if bf < -1:
            right_bf = self._balance_factor(node.right)

            # Case RR -> simple left rotation.
            if right_bf <= 0:
                self.rotation_case_counts["RR"] += 1
                return self._rotate_left(node)

            # Case RL -> right rotation on the right child, followed by left rotation.
            self.rotation_case_counts["RL"] += 1
            if node.right is None:
                raise RuntimeError("Caso RL inválido: el nodo no tiene hijo derecho.")
            self._rotate_right(node.right)
            return self._rotate_left(node)

        # If it was not unbalanced, return it as is.
        return node

    def _rebalance_upward_from(self, start_node: Optional[TreeNode]) -> None:
        """
        Rebalance from a node upward until reaching the root.

        This is the typical routine used after insertions or deletions.
        """
        current = start_node

        while current is not None:
            # Recalculate the current node locally.
            self._update_node_metrics_local(current)

            # If it is unbalanced, correct it.
            current = self._rebalance_at(current)

            # Continue towards the parent of the new local root.
            current = current.parent

    # -------------------------------------------------------------------------
    # Insertion
    # -------------------------------------------------------------------------
    def insert(self, flight: Any) -> TreeNode:
        """
        Insert a flight into the AVL tree.

        If the tree is in normal mode:
        - insert as a BST,
        - rebalance from the parent of the new node upward.

        If the tree is in stress mode:
        - insert as a BST,
        - DO NOT rebalance.
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
    # Deletion
    # -------------------------------------------------------------------------
    def delete(self, key: int) -> bool:
        """
        Delete a node by key.

        In normal mode, after deletion, AVL rebalancing is applied.
        In stress mode, only the BST structure is modified and metrics are recalculated.
        """
        node = self.search(key)
        if node is None:
            return False

        rebalance_points: list[Optional[TreeNode]] = []

        # Case 1 and 2: node with 0 or 1 child.
        if node.left is None:
            replacement = node.right
            rebalance_points.append(node.parent if node.parent is not None else replacement)
            self._transplant(node, replacement)

        elif node.right is None:
            replacement = node.left
            rebalance_points.append(node.parent if node.parent is not None else replacement)
            self._transplant(node, replacement)

        # Case 3: node with two children.
        else:
            successor = self.min_node(node.right)
            if successor is None:
                raise RuntimeError("No se encontró sucesor al eliminar un nodo con dos hijos.")

            old_successor_parent = successor.parent

            # If the successor is not the immediate right child,
            # first we remove it from its original position.
            if successor.parent != node:
                self._transplant(successor, successor.right)
                successor.right = node.right
                if successor.right is not None:
                    successor.right.parent = successor
                rebalance_points.append(old_successor_parent)

            # The successor now replaces the deleted node.
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
    # Cancelation of subtree
    # -------------------------------------------------------------------------
    def cancel_subtree(self, key: int) -> int:
        """
        Removes a node along with all its descendants.

        Difference from delete():
        - delete() preserves the rest of the tree and removes only a single node.
        - cancel_subtree() removes the entire subtree.

        This operation corresponds to the “cancel flight” requirement of the project.
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
    # Overall rebalancing
    # -------------------------------------------------------------------------
    def _postorder_nodes(self, node: Optional[TreeNode]) -> list[TreeNode]:
        """
        Returns a list of nodes in postorder.

        Postorder is useful for attempting to rebalance first the deeper levels
        and then moving upward toward the root.
        """
        if node is None:
            return []
        return self._postorder_nodes(node.left) + self._postorder_nodes(node.right) + [node]

    def rebalance_global(self) -> dict[str, int]:
        """
        Attempts to restore the AVL property over the entire tree.

        Designed to be used when exiting stress mode.

        Strategy:
        - traverse nodes in postorder,
        - detect imbalances,
        - apply rotations in cascade,
        - repeat until no changes occur.

        Returns
        -------
        dict[str, int]
            Summary of the structural cost of the global rebalance.
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

        # We prevent infinite loops by setting a generous limit.
        max_iterations = max(10, self.size() * 5)
        iteration = 0

        while iteration < max_iterations:
            iteration += 1
            changed = False

            # We take a snapshot in postorder of the current state.
            nodes = self._postorder_nodes(self.root)
            for node in nodes:
                # The node may still exist, but its position could have changed.
                # It remains valid as a reference to the object.
                old_root_key = self.root.key if self.root is not None else None
                old_node_parent = node.parent
                old_node_key = node.key

                self._update_node_metrics_local(node.left)
                self._update_node_metrics_local(node.right)
                self._update_node_metrics_local(node)

                if abs(self._balance_factor(node)) > 1:
                    self._rebalance_at(node)
                    changed = True

                # This comparison isn't perfect, but it helps highlight changes.
                if self.root is not None and self.root.key != old_root_key:
                    changed = True
                if node.parent != old_node_parent:
                    changed = True
                if node.key != old_node_key:
                    changed = True

            self.refresh_metadata()

            # If no changes occurred, the tree is now balanced.
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
    # Metrics and reports
    # -------------------------------------------------------------------------
    def rotation_summary(self) -> dict[str, int]:
        """
        Returns a complete summary of the accumulated rotations.
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
        Returns the total number of simple rotations executed.
        """
        return self.simple_rotation_counts["left"] + self.simple_rotation_counts["right"]

    # -------------------------------------------------------------------------
    # Basic audit of the AVL property
    # -------------------------------------------------------------------------
    def audit_avl(self) -> dict[str, Any]:
        """
        Traverses the tree and checks if it satisfies the AVL property.

        This method is very useful for the project milestone where
        'Verify AVL Property' is required and to report inconsistencies.

        Returns
        -------
        dict[str, Any]
            Report with general validity, errors and conflicting nodes.
        """
        issues: list[str] = []
        unbalanced_nodes: list[int] = []
        invalid_height_nodes: list[int] = []

        def _audit(node: Optional[TreeNode]) -> int:
            if node is None:
                return -1

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
        if self.root is None:
            overall_height = 0
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
    # API for teacher style compatibility
    # -------------------------------------------------------------------------
    def getBalanceFactor(self, node: Optional[TreeNode]) -> int:
        if node is None:
            return 0
        return self._balance_factor(node)

    def print_tree(self) -> None:
        self.pretty_print()

    # -------------------------------------------------------------------------
    # Auxiliary construction
    # -------------------------------------------------------------------------
    @classmethod
    def from_flights(cls, flights: list[FlightRecord], critical_depth_limit: Optional[int] = None) -> "AVL":
        """
        Constructs an AVL by inserting a list of flights one by one.
        """
        tree = cls(critical_depth_limit=critical_depth_limit)
        for flight in flights:
            tree.insert(flight)
        return tree
