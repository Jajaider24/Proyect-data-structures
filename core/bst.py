from __future__ import annotations

"""
core/bst.py

Implementation of a Binary Search Tree (BST) for the
SkyBalance AVL project.

Why build the BST first?
--------------------------------
Because the BST serves as a conceptual and functional foundation for:
1. Reusing search and traversal logic.
2. Compare it against the AVL when JSON is loaded in insert mode.
3. Have a simpler reference structure for testing business rules.

This file is designed to be highly educational:
- It includes extensive comments.
- It separates internal helpers from public methods.
- It recalculates tree metadata when changes occur.
"""

from collections import deque
from typing import Any, Optional

from models.flight_record import FlightRecord
from models.nodes import TreeNode


class BST:
    """
    Binary Search Tree.

    Main rule:
    - Every node in the left subtree has a key less than the parent node's key.
    - Every node in the right subtree has a key greater than the parent node's key.

    In this project the key is `flight.code_num`, that is,
    the normalized flight code.
    """

    def __init__(self) -> None:
        self.root: Optional[TreeNode] = None
        self._size: int = 0

    # -------------------------------------------------------------------------
    # Basic properties
    # -------------------------------------------------------------------------
    def is_empty(self) -> bool:
        """Returns True if the tree has no nodes."""
        return self.root is None

    def __len__(self) -> int:
        """Permite usar len(bst)."""
        return self._size

    def size(self) -> int:
        """Returns the number of nodes in the tree."""
        return self._size

    # -------------------------------------------------------------------------
    # Insertion
    # -------------------------------------------------------------------------
    def _build_placeholder_flight(self, value: Any) -> FlightRecord:
        """
        Builds a minimal flight from a key.

        This is used for compatibility with academic-style insertions
        (nodes based only on value).
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
        Converts various input types into a valid TreeNode.

        Supported inputs:
        - FlightRecord
        - TreeNode
        - objects with getValue() (compatibility with the Node class from the tutorial)
        - scalar values (int/str/float)
        """
        if isinstance(value, TreeNode):
            node = value
        elif isinstance(value, FlightRecord):
            node = TreeNode(flight=value)
        elif hasattr(value, "getValue"):
            node = TreeNode(flight=self._build_placeholder_flight(value.getValue()))
        else:
            node = TreeNode(flight=self._build_placeholder_flight(value))

        # Ensures clean insertion as a new node.
        node.left = None
        node.right = None
        node.parent = None
        return node

    def insert(self, flight: Any) -> TreeNode:
        """
        Inserts a flight into the BST.

        If the key already exists, an exception is raised.
        In the project, this is useful because flight codes must be unique.

        Parameters
        ----------
        flight : Any
            Can be a FlightRecord, TreeNode, Node (with getValue) or a value.

        Returns
        -------
        TreeNode
            Node created and inserted.
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

        # parent cannot be None here because root already existed.
        new_node.parent = parent
        if new_node.key < parent.key:
            parent.left = new_node
        else:
            parent.right = new_node

        self._size += 1
        self.refresh_metadata()
        return new_node

    # -------------------------------------------------------------------------
    # Search
    # -------------------------------------------------------------------------
    def search(self, key: int) -> Optional[TreeNode]:
        """
        Searches for a node by key.

        Parameters
        ----------
        key : int
            Standard flight code.

        Returns
        -------
        Optional[TreeNode]
            The node if it exists; otherwise, None.
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
        """Returns True if the key exists in the tree."""
        return self.search(key) is not None

    # -------------------------------------------------------------------------
    # Minimum, maximum, successor
    # -------------------------------------------------------------------------
    def min_node(self, node: Optional[TreeNode] = None) -> Optional[TreeNode]:
        """
        Returns the node with the smallest key.

        If no node is passed, it searches for the minimum in the entire tree.
        """
        current = node if node is not None else self.root
        if current is None:
            return None

        while current.left is not None:
            current = current.left
        return current

    def max_node(self, node: Optional[TreeNode] = None) -> Optional[TreeNode]:
        """
        Returns the node with the largest key.

        If no node is passed, it searches for the maximum in the entire tree.
        """
        current = node if node is not None else self.root
        if current is None:
            return None

        while current.right is not None:
            current = current.right
        return current

    def successor(self, node: TreeNode) -> Optional[TreeNode]:
        """
        Returns the inorder successor of a node.

        The inorder successor is the node with the smallest key greater than the current.
        It is very useful for the deletion of nodes with two children.
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
    # Elimination
    # -------------------------------------------------------------------------
    def delete(self, key: int) -> bool:
        """
        Deletes one node per key.

        Common cases of deletion in a BST:
        1. Leaf node.
        2. Node with a single child.
        3. Node with two children.

        Returns
        -------
        bool
            True if the node was deleted, False if it didn't exist.
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
        Deletes a node that has already been located.

        This method is internal. The public method `delete` first searches
        for the node and then calls this method.
        """
        # Case 1: The node is a leaf.
        if node.left is None and node.right is None:
            self._transplant(node, None)
            return

        # Case 2: The node has only a right child.
        if node.left is None:
            self._transplant(node, node.right)
            return

        # Case 2: The node has only a left child.
        if node.right is None:
            self._transplant(node, node.left)
            return

        # Case 3: The node has two children.
        # We search for the inorder successor (minimum of the right subtree).
        successor = self.min_node(node.right)
        if successor is None:
            raise RuntimeError("No se encontró sucesor para un nodo con hijo derecho.")

        # If the successor is not the immediate legitimate child,
        # The successor's subtree must be moved first.
        if successor.parent != node:
            self._transplant(successor, successor.right)
            successor.right = node.right
            if successor.right is not None:
                successor.right.parent = successor

        # Now we replace the node with its successor.
        self._transplant(node, successor)
        successor.left = node.left
        if successor.left is not None:
            successor.left.parent = successor

    def _transplant(self, old_node: TreeNode, new_node: Optional[TreeNode]) -> None:
        """
        Replaces a subtree with another.

        This helper is the classic technique to simplify deletion.

        Parameters
        ----------
        old_node : TreeNode
            Node to be replaced.
        new_node : Optional[TreeNode]
            New node that will take its place.
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
    # Subtree Deletion
    # -------------------------------------------------------------------------
    def cancel_subtree(self, key: int) -> int:
        """
        Removes a node and all its descendants.

        This operation differs from delete():
        - delete() removes a single node while preserving the BST structure.
        - cancel_subtree() removes the entire node along with all its children.

        This is exactly what the project requires when a flight is ‘canceled’.

        Returns
        -------
        int
            Number of nodes removed.
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
        """Count the number of nodes in a subtree."""
        if node is None:
            return 0
        return 1 + self._count_subtree_nodes(node.left) + self._count_subtree_nodes(node.right)

    # -------------------------------------------------------------------------
    # Traversals
    # -------------------------------------------------------------------------
    def inorder(self) -> list[FlightRecord]:
        """Inorder traversal: left, root, right."""
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
        """Preorder traversal: root, left, right."""
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
        """Postorder traversal: left, right, root."""
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
        Level-order traversal (BFS).

        Very useful for displaying the tree in an interface or debugging.
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
    # API for teacher style compatibility
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
        Height according to the teacher's code:
        - None = -1
        - leaf = 0
        """
        if node is None:
            return -1
        return 1 + max(self.calculateHeight(node.left), self.calculateHeight(node.right))

    # -------------------------------------------------------------------------
    # Structural metrics
    # -------------------------------------------------------------------------
    def height(self) -> int:
        """Height of the entire tree."""
        if self.root is None:
            return 0
        return self._compute_height(self.root)

    def _compute_height(self, node: Optional[TreeNode]) -> int:
        """
        Calculate the height of a node.

        Convention used:
        - node None -> height -1
        - leaf -> height 0
        """
        if node is None:
            return -1
        return 1 + max(self._compute_height(node.left), self._compute_height(node.right))

    def leaf_count(self) -> int:
        """Count the number of leaf nodes in the tree."""
        return self._leaf_count(self.root)

    def _leaf_count(self, node: Optional[TreeNode]) -> int:
        if node is None:
            return 0
        if node.left is None and node.right is None:
            return 1
        return self._leaf_count(node.left) + self._leaf_count(node.right)

    def depth_of_key(self, key: int) -> Optional[int]:
        """
        Returns the depth of a key.

        Depth of the root = 0.
        """
        node = self.search(key)
        if node is None:
            return None
        return node.flight.depth

    def root_key(self) -> Optional[int]:
        """Returns the key of the root or None if the tree is empty."""
        return self.root.key if self.root is not None else None

    # -------------------------------------------------------------------------
    # Metadata Update
    # -------------------------------------------------------------------------
    def refresh_metadata(self, critical_depth_limit: Optional[int] = None) -> None:
        """
        Recalculate depth, height, balance, and criticality for the entire tree.

        Although the BST does not balance like an AVL tree, we can still calculate the
        balance factor of each node as diagnostic information.

        This method is important because:
        - the project needs depth and height updated,
        - the criticality depends on the depth,
        - the JSON export must reflect the actual state of the tree.
        """

        def _walk(node: Optional[TreeNode], depth: int) -> int:
            if node is None:
                return -1

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
    # Validations
    # -------------------------------------------------------------------------
    def validate_bst_property(self) -> bool:
        """
        Verifies that the BST property is satisfied throughout the tree.

        This is useful for debugging and unit testing.
        """

        def _validate(node: Optional[TreeNode], low: Any, high: Any) -> bool:
            if node is None:
                return True

            if (low is not None and node.key <= low) or (high is not None and node.key >= high):
                return False

            return _validate(node.left, low, node.key) and _validate(node.right, node.key, high)

        return _validate(self.root, None, None)

    # -------------------------------------------------------------------------
    # Export and Representation
    # -------------------------------------------------------------------------
    def to_topology_dict(self) -> Optional[dict[str, Any]]:
        """
        Export the entire tree in a hierarchical format.

        If the tree is empty, returns None.
        """
        if self.root is None:
            return None
        return self.root.to_topology_dict()

    def to_insertion_list(self) -> list[dict[str, Any]]:
        """
        Export the tree as a list of flights in level-order traversal.

        It does not reconstruct the same topology, but it does serve as a
        ‘insertion list’ format for testing or simple persistence.
        """
        return [flight.to_dict() for flight in self.level_order()]

    def pretty_print(self) -> None:
        """
        Prints the tree in the console in a horizontal layout.

        Useful during development before building the Flet interface.
        """

        def _print(node: Optional[TreeNode], level: int = 0, prefix: str = "R: ") -> None:
            if node is None:
                return

            _print(node.right, level + 1, "D: ")
            print("    " * level + f"{prefix}{node.key} (h={node.flight.height}, bf={node.flight.balance_factor})")
            _print(node.left, level + 1, "I: ")

        _print(self.root)

    # -------------------------------------------------------------------------
    # Auxiliary Construction from Collections
    # -------------------------------------------------------------------------
    @classmethod
    def from_flights(cls, flights: list[FlightRecord]) -> "BST":
        """
        Builds a BST by inserting a list of flights one by one.
        """
        tree = cls()
        for flight in flights:
            tree.insert(flight)
        return tree
