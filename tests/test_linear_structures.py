import unittest

from core.queue import Cola
from core.stack import Pila


class TestLinearStructures(unittest.TestCase):
    def test_pila_lifo(self) -> None:
        pila = Pila()
        pila.apilar(10)
        pila.apilar(20)

        self.assertEqual(pila.obtenerElemento(), 20)
        self.assertEqual(pila.desapilar(), 20)
        self.assertEqual(pila.desapilar(), 10)
        self.assertTrue(pila.estaVacia())

    def test_cola_fifo(self) -> None:
        cola = Cola()
        cola.encolar("A")
        cola.encolar("B")

        self.assertEqual(cola.obtenerElemento(), "A")
        self.assertEqual(cola.desencolar(), "A")
        self.assertEqual(cola.desencolar(), "B")
        self.assertTrue(cola.estaVacia())


if __name__ == "__main__":
    unittest.main()
