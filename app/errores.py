"""Traducción de los errores de validación a mensajes claros en español."""

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

MENSAJE_ENTERO = "Debe ser un número entero."
MENSAJE_NUMERO = "Debe ser un número válido."
MENSAJE_FECHA = "Debe ser una fecha con formato AAAA-MM-DD."

# Plantillas por tipo de error de Pydantic; las llaves se rellenan con el contexto del error.
PLANTILLAS_DE_MENSAJE = {
    "missing": "Campo obligatorio.",
    "enum": "Valor no permitido. Valores válidos: {expected}.",
    "greater_than": "Debe ser mayor que {gt}.",
    "extra_forbidden": "Campo no reconocido.",
    "int_parsing": MENSAJE_ENTERO,
    "int_from_float": MENSAJE_ENTERO,
    "int_type": MENSAJE_ENTERO,
    "decimal_parsing": MENSAJE_NUMERO,
    "decimal_type": MENSAJE_NUMERO,
    "date_parsing": MENSAJE_FECHA,
    "date_from_datetime_parsing": MENSAJE_FECHA,
    "date_type": MENSAJE_FECHA,
    "list_type": "Debe ser una lista.",
    "json_invalid": "El cuerpo no es un JSON válido.",
}
UBICACION_CUERPO = "body"
SEPARADOR_CAMPO = "."


def mensaje_en_espanol(error: dict) -> str:
    """Devuelve el mensaje en español del error, o el original si no hay plantilla."""
    plantilla = PLANTILLAS_DE_MENSAJE.get(error["type"])
    if plantilla is None:
        return error["msg"]
    return plantilla.format(**error.get("ctx", {}))


def nombre_del_campo(ubicacion: tuple) -> str:
    """Convierte la ubicación del error en una ruta legible, sin el prefijo 'body'."""
    partes = [str(parte) for parte in ubicacion if parte != UBICACION_CUERPO]
    return SEPARADOR_CAMPO.join(partes)


def manejar_error_de_validacion(_: Request, error: RequestValidationError) -> JSONResponse:
    """Responde 422 con la lista de campos inválidos y su explicación."""
    detalle = [
        {"campo": nombre_del_campo(problema["loc"]), "mensaje": mensaje_en_espanol(problema)}
        for problema in error.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content={"detalle": detalle}
    )
