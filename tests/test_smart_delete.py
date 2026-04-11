import unittest

from api import state
from api.routes.flights import delete_least_profitable
from controllers.economics_controller import least_profitable_flight
from core.avl import AVL
from core.bst import BST
from models.flight_record import FlightRecord


def make_flight(code: int, base_price: float, passengers: int = 1) -> FlightRecord:
    return FlightRecord(
        code_raw=code,
        origin="A",
        destination="B",
        departure_time="08:00",
        base_price=base_price,
        passengers=passengers,
        priority="MEDIA",
        promotion=0.0,
        alert="NORMAL",
    )


def reset_state() -> None:
    state.avl_tree = AVL()
    state.bst_tree = BST()
    state.undo_manager.clear()
    state.version_manager.clear()
    state.queue_manager.clear()


class TestSmartDelete(unittest.TestCase):
    def setUp(self) -> None:
        reset_state()

    def test_least_profitable_uses_tie_breakers(self) -> None:
        # Balanced insertion order to produce multiple depths.
        for code in [50, 30, 70, 20, 40, 60, 80]:
            if code in {30, 20, 40}:
                flight = make_flight(code, base_price=10.0, passengers=1)
            else:
                flight = make_flight(code, base_price=100.0, passengers=1)
            state.avl_tree.insert(flight)

        candidate = least_profitable_flight(state.avl_tree)
        self.assertIsNotNone(candidate)
        # Same profitability in 30,20,40 -> choose deepest first (20/40), then higher code.
        self.assertEqual(candidate["codigoNormalizado"], 40)

    def test_delete_least_profitable_cancels_subtree(self) -> None:
        # Candidate 30 has the worst profitability and owns descendants 20 and 40.
        data = [
            make_flight(50, 120.0),
            make_flight(30, 5.0),
            make_flight(70, 130.0),
            make_flight(20, 90.0),
            make_flight(40, 95.0),
        ]
        for flight in data:
            state.avl_tree.insert(flight)
            state.bst_tree.insert(make_flight(flight.code_num, flight.base_price, flight.passengers))

        before_count = state.avl_tree.size()
        result = delete_least_profitable()

        self.assertEqual(result["selected"]["codigoNormalizado"], 30)
        self.assertGreaterEqual(result["removed_avl"], 3)
        self.assertEqual(result["removed_avl"], result["removed_bst"])
        self.assertEqual(state.avl_tree.size(), before_count - result["removed_avl"])
        self.assertTrue(state.undo_manager.can_undo())


if __name__ == "__main__":
    unittest.main()
