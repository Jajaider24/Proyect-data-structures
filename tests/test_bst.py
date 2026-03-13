import unittest

from core.bst import BST
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


class TestBST(unittest.TestCase):
	def test_insert_and_search(self) -> None:
		tree = BST()
		for code in [50, 30, 70, 20, 40, 60, 80]:
			tree.insert(build_flight(code))

		self.assertTrue(tree.contains(40))
		self.assertIsNone(tree.search(999))
		self.assertEqual(tree.size(), 7)

	def test_delete_leaf_one_child_two_children(self) -> None:
		tree = BST()
		for code in [50, 30, 70, 20, 40, 60, 80, 65]:
			tree.insert(code)

		# Hoja
		self.assertTrue(tree.delete(20))
		self.assertFalse(tree.contains(20))

		# Un hijo (60 tiene hijo derecho 65)
		self.assertTrue(tree.delete(60))
		self.assertFalse(tree.contains(60))
		self.assertTrue(tree.contains(65))

		# Dos hijos (raíz)
		self.assertTrue(tree.delete(50))
		self.assertFalse(tree.contains(50))
		self.assertTrue(tree.validate_bst_property())

		inorder_keys = [f.code_num for f in tree.inorder()]
		self.assertEqual(inorder_keys, sorted(inorder_keys))

	def test_professor_style_methods(self) -> None:
		tree = BST()
		for code in [50, 30, 70, 20, 40, 60, 80]:
			tree.insert(Node(code))

		self.assertEqual(tree.breadthFirstSearch(), [50, 30, 70, 20, 40, 60, 80])
		self.assertEqual(tree.preOrderTraversal(), [50, 30, 20, 40, 70, 60, 80])
		self.assertEqual(tree.inOrderTraversal(), [20, 30, 40, 50, 60, 70, 80])
		self.assertEqual(tree.posOrderTraversal(), [20, 40, 30, 60, 80, 70, 50])

		root = tree.getRoot()
		self.assertIsNotNone(root)
		self.assertEqual(tree.calculateHeight(root), 2)


if __name__ == "__main__":
	unittest.main()
