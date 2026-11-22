"""Valores permitidos del dominio de inventario.

Se conservan en inglés (BUY, SELL, COAL...) porque son los valores exactos que
usa el aplicativo de inventario y que viajan en el JSON de la API.
"""

from enum import StrEnum


class TipoTransaccion(StrEnum):
    """Tipo de movimiento: BUY suma al inventario y SELL resta."""

    BUY = "BUY"
    SELL = "SELL"


class Producto(StrEnum):
    """Los cinco productos que maneja el aplicativo de inventario."""

    COAL = "COAL"
    GOLD = "GOLD"
    IRON = "IRON"
    TIMBER = "TIMBER"
    ALUMINIUM = "ALUMINIUM"
