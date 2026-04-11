import unittest

from api import state
from api.routes.flights import set_critical_depth_limit
from api.schemas import CriticalDepthPayload
from core.avl import AVL
from core.bst import BST
from models.flight_record import FlightRecord


def make_flight(code: int, base_price: float) -> FlightRecord:
    return FlightRecord(
        code_raw=code,
        origin="A",
        destination="B",
        departure_time="08:00",
        base_price=base_price,
        passengers=2,
        priority="MEDIA",
        promotion=0.0,
        alert="NORMAL",
    )


def reset_state() -> None:
    state.avl_tree = AVL()
    state.bst_tree = BST()


class TestCriticalDepthLimit(unittest.TestCase):
    def setUp(self) -> None:
        reset_state()
        for code in [50, 30, 70]:
            state.avl_tree.insert(make_flight(code, 100.0))
            state.bst_tree.insert(make_flight(code, 100.0))

    def test_apply_limit_marks_critical_and_updates_price(self) -> None:
        result = set_critical_depth_limit(CriticalDepthPayload(limit=0))
        self.assertEqual(result["critical_depth_limit"], 0)

        left_node = state.avl_tree.search(30)
        self.assertIsNotNone(left_node)
        self.assertTrue(left_node.flight.is_critical)
        self.assertEqual(left_node.flight.final_price, 125.0)

    def test_clear_limit_removes_critical_penalty(self) -> None:
        set_critical_depth_limit(CriticalDepthPayload(limit=0))
        result = set_critical_depth_limit(CriticalDepthPayload(limit=None))

        self.assertIsNone(result["critical_depth_limit"])
        left_node = state.avl_tree.search(30)
        self.assertIsNotNone(left_node)
        self.assertFalse(left_node.flight.is_critical)
        self.assertEqual(left_node.flight.final_price, 100.0)


if __name__ == "__main__":
    unittest.main()
