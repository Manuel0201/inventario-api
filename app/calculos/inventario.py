"""Cálculos puros de stock y rentabilidad.

Son funciones sin base de datos ni web: reciben datos y devuelven resultados, por
eso se pueden probar solas y reutilizar desde cualquier capa.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.enumeraciones import Producto, TipoTransaccion

CERO_DINERO = Decimal(0)
STOCK_INICIAL = 0

# BUY aumenta el inventario (+1) y SELL lo disminuye (-1).
EFECTO_EN_STOCK = {TipoTransaccion.BUY: 1, TipoTransaccion.SELL: -1}


@dataclass(frozen=True)
class Transaccion:
    """Un movimiento de inventario ya validado."""

    tipo: TipoTransaccion
    fecha: date
    producto: Producto
    cantidad: int
    valor_unitario: Decimal


@dataclass(frozen=True)
class ProductosMasRentables:
    """Producto(s) con mayor rentabilidad; vacío si no hubo ventas."""

    productos: tuple[Producto, ...]
    rentabilidad: Decimal | None

    @property
    def hay_empate(self) -> bool:
        """Hay empate cuando más de un producto comparte la rentabilidad máxima."""
        return len(self.productos) > 1


def calcular_stock_por_producto(transacciones: list[Transaccion]) -> dict[Producto, int]:
    """Stock final por producto: suma las BUY y resta las SELL.

    Incluye siempre los cinco productos; sin transacciones el stock es 0 y puede
    ser negativo si las ventas superan las compras.
    """
    stock = {producto: STOCK_INICIAL for producto in Producto}
    for transaccion in transacciones:
        stock[transaccion.producto] += EFECTO_EN_STOCK[transaccion.tipo] * transaccion.cantidad
    return stock


def calcular_rentabilidad_por_producto(
    transacciones: list[Transaccion],
) -> dict[Producto, Decimal]:
    """Rentabilidad por producto: suma de cantidad x valor unitario solo en las SELL."""
    rentabilidad = {producto: CERO_DINERO for producto in Producto}
    for transaccion in transacciones:
        if transaccion.tipo is TipoTransaccion.SELL:
            rentabilidad[transaccion.producto] += transaccion.cantidad * transaccion.valor_unitario
    return rentabilidad


def identificar_productos_mas_rentables(
    rentabilidad: dict[Producto, Decimal],
) -> ProductosMasRentables:
    """Devuelve todos los productos que comparten la rentabilidad máxima.

    Si ningún producto vendió (máximo 0) no hay "más rentable": lista vacía y None.
    Los empatados se ordenan alfabéticamente para que la respuesta sea predecible.
    """
    maximo = max(rentabilidad.values())
    if maximo <= CERO_DINERO:
        return ProductosMasRentables(productos=(), rentabilidad=None)
    empatados = sorted(
        (producto for producto, valor in rentabilidad.items() if valor == maximo),
        key=lambda producto: producto.value,
    )
    return ProductosMasRentables(productos=tuple(empatados), rentabilidad=maximo)
