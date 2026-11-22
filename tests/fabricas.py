"""Ayudas para construir transacciones de prueba sin repetir código."""

from datetime import date
from decimal import Decimal

from app.calculos.inventario import Transaccion
from app.enumeraciones import Producto, TipoTransaccion

FECHA_DE_PRUEBA = date(2020, 5, 5)


def crear_transaccion(
    tipo: TipoTransaccion,
    producto: Producto,
    cantidad: int,
    valor_unitario: int,
) -> Transaccion:
    """Crea una transacción de prueba con la fecha fija."""
    return Transaccion(
        tipo=tipo,
        fecha=FECHA_DE_PRUEBA,
        producto=producto,
        cantidad=cantidad,
        valor_unitario=Decimal(valor_unitario),
    )


def crear_transacciones_de_ejemplo() -> list[Transaccion]:
    """Cinco transacciones con resultado conocido.

    Stock: COAL 70, GOLD 15, IRON -10, TIMBER 0, ALUMINIUM 0.
    Rentabilidad: COAL 1500, GOLD 1500 (empatan), IRON 1000.
    """
    return [
        crear_transaccion(TipoTransaccion.BUY, Producto.COAL, 100, 10),
        crear_transaccion(TipoTransaccion.SELL, Producto.COAL, 30, 50),
        crear_transaccion(TipoTransaccion.BUY, Producto.GOLD, 20, 200),
        crear_transaccion(TipoTransaccion.SELL, Producto.GOLD, 5, 300),
        crear_transaccion(TipoTransaccion.SELL, Producto.IRON, 10, 100),
    ]
