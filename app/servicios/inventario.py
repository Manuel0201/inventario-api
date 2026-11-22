"""Servicio de inventario: coordina los cálculos y arma el resultado completo."""

from dataclasses import dataclass
from decimal import Decimal

from app.calculos.inventario import (
    Transaccion,
    calcular_rentabilidad_por_producto,
    calcular_stock_por_producto,
    identificar_productos_mas_rentables,
)
from app.enumeraciones import Producto
from app.esquemas import TransaccionEntrada


@dataclass(frozen=True)
class ResultadoInventario:
    """Resultado del análisis; los nombres coinciden con los de la respuesta de la API."""

    stock_por_producto: dict[Producto, int]
    rentabilidad_por_producto: dict[Producto, Decimal]
    productos_mas_rentables: tuple[Producto, ...]
    rentabilidad_maxima: Decimal | None
    hay_empate: bool


def convertir_a_transaccion(entrada: TransaccionEntrada) -> Transaccion:
    """Pasa una transacción validada por Pydantic al tipo simple que usan los cálculos."""
    return Transaccion(
        tipo=entrada.tipo,
        fecha=entrada.fecha,
        producto=entrada.producto,
        cantidad=entrada.cantidad,
        valor_unitario=entrada.valor_unitario,
    )


def analizar_transacciones(entradas: list[TransaccionEntrada]) -> ResultadoInventario:
    """Calcula stock, rentabilidad y producto(s) más rentable(s) de las transacciones."""
    transacciones = [convertir_a_transaccion(entrada) for entrada in entradas]
    rentabilidad = calcular_rentabilidad_por_producto(transacciones)
    mas_rentables = identificar_productos_mas_rentables(rentabilidad)
    return ResultadoInventario(
        stock_por_producto=calcular_stock_por_producto(transacciones),
        rentabilidad_por_producto=rentabilidad,
        productos_mas_rentables=mas_rentables.productos,
        rentabilidad_maxima=mas_rentables.rentabilidad,
        hay_empate=mas_rentables.hay_empate,
    )
