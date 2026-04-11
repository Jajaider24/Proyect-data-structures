import unittest

from core.avl import AVL
from core.bst import BST
from models.flight_record import FlightRecord


def make_flight(code: int) -> FlightRecord:
    return FlightRecord(
        code_raw=code,
        origin="A",
        destination="B",
        departure_time="08:00",
        base_price=100.0,
        passengers=1,
        priority="MEDIA",
        promotion=0.0,
        alert="NORMAL",
    )


class TestHeightDefinition(unittest.TestCase):
    def test_empty_tree_height_is_zero(self) -> None:
        tree = BST()
        self.assertEqual(tree.height(), 0)

    def test_leaf_height_is_zero_and_equals_tree_height(self) -> None:
        tree = BST()
        tree.insert(make_flight(50))

        root = tree.search(50)
        self.assertIsNotNone(root)
        self.assertEqual(tree.height(), 0)
        self.assertEqual(root.flight.height, 0)

    def test_root_height_counts_edges_to_farthest_node(self) -> None:
        tree = BST()
        for code in [50, 30, 20]:
            tree.insert(make_flight(code))

        root = tree.search(50)
        leaf = tree.search(20)
        self.assertIsNotNone(root)
        self.assertIsNotNone(leaf)
        self.assertEqual(tree.height(), 2)
        self.assertEqual(root.flight.height, 2)
        self.assertEqual(leaf.flight.height, 0)

    def test_avl_root_height_matches_tree_height(self) -> None:
        tree = AVL()
        for code in [50, 30, 70, 20, 40, 60, 80]:
            tree.insert(make_flight(code))

        self.assertIsNotNone(tree.root)
        self.assertEqual(tree.height(), tree.root.flight.height)


if __name__ == "__main__":
    unittest.main()
