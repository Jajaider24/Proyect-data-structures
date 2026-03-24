import unittest

from core.avl import AVL
from models import FlightRecord


def build_flight(code: int, base_price: float = 100.0, promotion: float = 0.0, passengers: int = 10) -> FlightRecord:
	return FlightRecord(
		code_raw=code,
		origin="A",
		destination="B",
		departure_time="10:00",
		base_price=base_price,
		passengers=passengers,
		promotion=promotion,
	)


class TestRules(unittest.TestCase):
	def test_critical_depth_affects_final_price(self) -> None:
		tree = AVL(critical_depth_limit=1)
		for code in [40, 20, 60, 10, 30, 50, 70, 5]:
			tree.insert(build_flight(code, base_price=200, promotion=20))

		deep_node = tree.search(5)
		self.assertIsNotNone(deep_node)

		# Profundidad > 1 debe marcarse crítica.
		self.assertTrue(deep_node.flight.is_critical)
		# Precio final = base - promoción + recargo crítico (25% base)
		self.assertEqual(deep_node.flight.final_price, 230.0)

	def test_profitability_uses_updated_price(self) -> None:
		flight = build_flight(code=100, base_price=100, promotion=10, passengers=2)

		flight.update_tree_metrics(depth=3, height=1, balance_factor=0)
		flight.update_critical_status(critical_depth_limit=1)

		# final_price = 100 - 10 + 25 = 115
		self.assertEqual(flight.final_price, 115.0)
		# rentabilidad = pasajeros*precioFinal - promoción + penalización
		self.assertEqual(flight.economic_profitability(), 245.0)


if __name__ == "__main__":
	unittest.main()
