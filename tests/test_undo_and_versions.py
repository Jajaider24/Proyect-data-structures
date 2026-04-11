import unittest

from api import state
from api.routes.export import undo_last_action
from api.routes.flights import set_critical_depth_limit
from api.routes.versions import restore_version, save_version
from api.schemas import CriticalDepthPayload, VersionPayload
from core.avl import AVL
from core.bst import BST
from models.flight_record import FlightRecord


def make_flight(code: int, base_price: float = 100.0) -> FlightRecord:
    return FlightRecord(
        code_raw=code,
        origin="A",
        destination="B",
        departure_time="08:00",
        base_price=base_price,
        passengers=1,
        priority="MEDIA",
        promotion=0.0,
        alert="NORMAL",
    )


def reset_state() -> None:
    state.avl_tree = AVL()
    state.bst_tree = BST()
    state.undo_manager.clear()
    state.version_manager.clear()


class TestUndoAndVersions(unittest.TestCase):
    def setUp(self) -> None:
        reset_state()

    def test_undo_restores_previous_snapshot(self) -> None:
        state.avl_tree.insert(make_flight(50))
        state.bst_tree.insert(make_flight(50))

        set_critical_depth_limit(CriticalDepthPayload(limit=0))
        state.avl_tree.insert(make_flight(30))
        state.bst_tree.insert(make_flight(30))
        state.undo_manager.push_snapshot(state.avl_tree, action="before_insert")

        state.avl_tree.insert(make_flight(70))
        state.bst_tree.insert(make_flight(70))

        self.assertEqual(state.avl_tree.size(), 3)
        result = undo_last_action()

        self.assertEqual(result["restored_action"], "before_insert")
        self.assertEqual(state.avl_tree.size(), 2)

        restored_node = state.avl_tree.search(30)
        self.assertIsNotNone(restored_node)
        self.assertTrue(restored_node.flight.is_critical)
        self.assertEqual(restored_node.flight.final_price, 125.0)

    def test_restore_named_version(self) -> None:
        state.avl_tree.insert(make_flight(50))
        state.bst_tree.insert(make_flight(50))

        save_version(VersionPayload(name="baseline", overwrite=False))

        state.avl_tree.insert(make_flight(30))
        state.bst_tree.insert(make_flight(30))
        self.assertEqual(state.avl_tree.size(), 2)

        result = restore_version("baseline")

        self.assertEqual(result["name"], "baseline")
        self.assertEqual(state.avl_tree.size(), 1)
        self.assertIsNone(state.avl_tree.search(30))


if __name__ == "__main__":
    unittest.main()
