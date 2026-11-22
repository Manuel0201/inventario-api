"""Router de inventario: solo declara la ruta y delega al servicio (sin lógica de negocio)."""

from fastapi import APIRouter, status

from app.constantes import ETIQUETA_INVENTARIO, PREFIJO_INVENTARIO, RUTA_ANALISIS
from app.esquemas import RespuestaError, RespuestaInventario, SolicitudInventario
from app.servicios import inventario as servicio_inventario

router = APIRouter(prefix=PREFIJO_INVENTARIO, tags=[ETIQUETA_INVENTARIO])


@router.post(
    RUTA_ANALISIS,
    response_model=RespuestaInventario,
    status_code=status.HTTP_200_OK,
    summary="Analizar transacciones de inventario",
    description=(
        "Recibe las transacciones y devuelve el stock final de los cinco productos (BUY suma, "
        "SELL resta), la rentabilidad de cada uno (cantidad x valor unitario solo de las SELL) y "
        "el/los más rentables. Si dos o más productos empatan se devuelven todos. Con una lista "
        "vacía todos los stocks son 0 y no hay producto más rentable."
    ),
    responses={
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "model": RespuestaError,
            "description": (
                "Entrada inválida: tipo distinto de BUY/SELL, producto no reconocido, cantidad o "
                "valor unitario no positivos, fecha inválida o campos faltantes."
            ),
        }
    },
)
def analizar_inventario(solicitud: SolicitudInventario):
    return servicio_inventario.analizar_transacciones(solicitud.transacciones)
