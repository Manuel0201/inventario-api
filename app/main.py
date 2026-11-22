"""Punto de entrada de la API de inventario."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.constantes import DESCRIPCION_API, RUTA_DOCUMENTACION, TITULO_API, VERSION_API
from app.errores import manejar_error_de_validacion
from app.routers import inventario

app = FastAPI(
    title=TITULO_API,
    version=VERSION_API,
    description=DESCRIPCION_API,
    docs_url=RUTA_DOCUMENTACION,
    redoc_url=None,
)
app.include_router(inventario.router)
app.add_exception_handler(RequestValidationError, manejar_error_de_validacion)
