from core.avl import AVL
from core.bst import BST
from services.queue_manager import InsertionQueueManager
from services.undo_manager import UndoManager
from services.version_manager import VersionManager

# Estado en memoria para la primera version de la API.
avl_tree = AVL()
bst_tree = BST()
undo_manager = UndoManager(max_history=100)
version_manager = VersionManager()
queue_manager = InsertionQueueManager()
