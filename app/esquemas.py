"""Esquemas de entrada y salida de la API (validación y documentación OpenAPI)."""

from datetime import date
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from app.enumeraciones import Producto, TipoTransaccion

# El dinero se calcula con Decimal (exacto) y se entrega en el JSON como número.
Dinero = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


class TransaccionEntrada(BaseModel):
    """Una transacción de compra o venta."""

    model_config = ConfigDict(extra="forbid")

    tipo: TipoTransaccion = Field(description="BUY suma al inventario; SELL resta.")
    fecha: date = Field(
        description="Fecha de la transacción (AAAA-MM-DD).", examples=["2020-05-05"]
    )
    producto: Producto = Field(description="Producto: COAL, GOLD, IRON, TIMBER o ALUMINIUM.")
    cantidad: int = Field(gt=0, description="Unidades de la transacción (entero mayor que 0).")
    valor_unitario: Decimal = Field(
        gt=0, allow_inf_nan=False, description="Valor de cada unidad (mayor que 0)."
    )


class SolicitudInventario(BaseModel):
    """Cuerpo de la petición: la lista de transacciones (puede venir vacía)."""

    model_config = ConfigDict(extra="forbid")

    transacciones: list[TransaccionEntrada] = Field(description="Transacciones a analizar.")


class RespuestaInventario(BaseModel):
    """Resultado del análisis de inventario."""

    model_config = ConfigDict(from_attributes=True)

    stock_por_producto: dict[Producto, int] = Field(
        description="Stock final de los cinco productos (BUY menos SELL); puede ser negativo."
    )
    rentabilidad_por_producto: dict[Producto, Dinero] = Field(
        description="Suma de cantidad x valor unitario de las SELL de cada producto."
    )
    productos_mas_rentables: list[Producto] = Field(
        description="Producto(s) más rentable(s); varios si empatan, vacío si no hubo ventas."
    )
    rentabilidad_maxima: Dinero | None = Field(
        description="Rentabilidad del/los más rentable(s); null si no hubo ventas."
    )
    hay_empate: bool = Field(
        description="true si más de un producto comparte la rentabilidad máxima."
    )


class DetalleError(BaseModel):
    """Un problema encontrado en la petición."""

    campo: str = Field(
        description="Ruta del campo con error.", examples=["transacciones.0.cantidad"]
    )
    mensaje: str = Field(description="Explicación del error.", examples=["Debe ser mayor que 0."])


class RespuestaError(BaseModel):
    """Respuesta de error de validación (422)."""

    detalle: list[DetalleError] = Field(description="Lista de errores encontrados.")
