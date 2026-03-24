from __future__ import annotations

from typing import Any
import re


def normalize_flight_code(code: Any) -> int:
    """
    Convierte distintos formatos de codigo de vuelo en una clave numerica.
    """
    if isinstance(code, int):
        return code

    if isinstance(code, float):
        if code.is_integer():
            return int(code)
        raise ValueError(f"El codigo numerico no es entero: {code}")

    code_str = str(code).strip()
    digits = re.findall(r"\d+", code_str)

    if not digits:
        raise ValueError(f"No se pudo normalizar el codigo de vuelo: {code}")

    return int("".join(digits))
