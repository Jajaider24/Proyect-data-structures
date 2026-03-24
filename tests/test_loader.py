import unittest

from models import FlightRecord, normalize_flight_code


class TestLoaderAndNormalization(unittest.TestCase):
	def test_normalize_flight_code(self) -> None:
		self.assertEqual(normalize_flight_code("SB400"), 400)
		self.assertEqual(normalize_flight_code("AVL-275"), 275)
		self.assertEqual(normalize_flight_code(500), 500)
		self.assertEqual(normalize_flight_code("500"), 500)

	def test_flightrecord_from_dict_roundtrip(self) -> None:
		raw = {
			"codigo": "SB777",
			"origen": "Bogota",
			"destino": "Cali",
			"horaSalida": "12:00",
			"precioBase": 350,
			"pasajeros": 90,
			"prioridad": "ALTA",
			"promocion": 25,
			"alerta": "NORMAL",
		}

		record = FlightRecord.from_dict(raw)
		as_dict = record.to_dict()

		self.assertEqual(record.code_num, 777)
		self.assertEqual(as_dict["codigoNormalizado"], 777)
		self.assertEqual(as_dict["origen"], "Bogota")
		self.assertEqual(as_dict["destino"], "Cali")


if __name__ == "__main__":
	unittest.main()
