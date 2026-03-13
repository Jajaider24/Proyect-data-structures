import unittest

from core.avl import AVL
from core.models import FlightRecord, Node


def build_flight(code: int) -> FlightRecord:
	return FlightRecord(
		code_raw=code,
		origin="A",
		destination="B",
		departure_time="10:00",
		base_price=100,
		passengers=10,
	)


class TestAVL(unittest.TestCase):
	def test_ll_rotation(self) -> None:
		tree = AVL()
		for code in [30, 20, 10]:
			tree.insert(code)

		self.assertEqual(tree.root_key(), 20)
		self.assertEqual(tree.rotation_case_counts["LL"], 1)
		self.assertTrue(tree.audit_avl()["is_valid_avl"])

	def test_rr_rotation(self) -> None:
		tree = AVL()
		for code in [10, 20, 30]:
			tree.insert(code)

		self.assertEqual(tree.root_key(), 20)
		self.assertEqual(tree.rotation_case_counts["RR"], 1)
		self.assertTrue(tree.audit_avl()["is_valid_avl"])

	def test_lr_rotation(self) -> None:
		tree = AVL()
		for code in [30, 10, 20]:
			tree.insert(code)

		self.assertEqual(tree.root_key(), 20)
		self.assertEqual(tree.rotation_case_counts["LR"], 1)
		self.assertTrue(tree.audit_avl()["is_valid_avl"])

	def test_rl_rotation(self) -> None:
		tree = AVL()
		for code in [10, 30, 20]:
			tree.insert(code)

		self.assertEqual(tree.root_key(), 20)
		self.assertEqual(tree.rotation_case_counts["RL"], 1)
		self.assertTrue(tree.audit_avl()["is_valid_avl"])

	def test_delete_keeps_avl_property(self) -> None:
		tree = AVL()
		for code in [50, 30, 70, 20, 40, 60, 80, 10, 25, 35, 45]:
			tree.insert(build_flight(code))

		self.assertTrue(tree.delete(20))
		self.assertTrue(tree.delete(70))
		self.assertFalse(tree.delete(999))

		report = tree.audit_avl()
		self.assertTrue(report["is_valid_avl"])
		self.assertTrue(tree.validate_bst_property())

	def test_professor_style_compatibility(self) -> None:
		tree = AVL()
		for code in [40, 20, 60, 10, 30, 50, 70]:
			tree.insert(Node(code))

		root = tree.getRoot()
		self.assertIsNotNone(root)
		self.assertEqual(tree.getBalanceFactor(root), 0)
		self.assertEqual(tree.inOrderTraversal(), [10, 20, 30, 40, 50, 60, 70])


if __name__ == "__main__":
	unittest.main()
