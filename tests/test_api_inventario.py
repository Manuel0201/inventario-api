"""Pruebas de integración del endpoint POST /inventario/analisis (contrato de respuesta)."""

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app

RUTA_ANALISIS = "/inventario/analisis"
RUTA_DOCUMENTACION = "/api-docs"
CLIENTE = TestClient(app)

FECHA_JSON = "2020-05-05"


def crear_transaccion_json(tipo: str, producto: str, cantidad: int, valor_unitario) -> dict:
    """Arma una transacción tal como viaja en el JSON de la petición."""
    return {
        "tipo": tipo,
        "fecha": FECHA_JSON,
        "producto": producto,
        "cantidad": cantidad,
        "valor_unitario": valor_unitario,
    }


TRANSACCION_VALIDA = crear_transaccion_json("BUY", "COAL", 10, 5)
TRANSACCIONES_DE_EJEMPLO = [
    crear_transaccion_json("BUY", "COAL", 100, 10),
    crear_transaccion_json("SELL", "COAL", 30, 50),
    crear_transaccion_json("BUY", "GOLD", 20, 200),
    crear_transaccion_json("SELL", "GOLD", 5, 300),
    crear_transaccion_json("SELL", "IRON", 10, 100),
]


def enviar(transacciones: list[dict]):
    return CLIENTE.post(RUTA_ANALISIS, json={"transacciones": transacciones})


def con_cambio(**cambios) -> dict:
    return {**TRANSACCION_VALIDA, **cambios}


class TestAnalisisExitoso:
    def test_contrato_completo_con_empate(self):
        respuesta = enviar(TRANSACCIONES_DE_EJEMPLO)

        assert respuesta.status_code == status.HTTP_200_OK
        assert respuesta.json() == {
            "stock_por_producto": {
                "COAL": 70,
                "GOLD": 15,
                "IRON": -10,
                "TIMBER": 0,
                "ALUMINIUM": 0,
            },
            "rentabilidad_por_producto": {
                "COAL": 1500.0,
                "GOLD": 1500.0,
                "IRON": 1000.0,
                "TIMBER": 0.0,
                "ALUMINIUM": 0.0,
            },
            "productos_mas_rentables": ["COAL", "GOLD"],
            "rentabilidad_maxima": 1500.0,
            "hay_empate": True,
        }

    def test_un_unico_producto_mas_rentable(self):
        respuesta = enviar([con_cambio(tipo="SELL", producto="IRON", cantidad=2, valor_unitario=7)])

        cuerpo = respuesta.json()
        assert cuerpo["productos_mas_rentables"] == ["IRON"]
        assert cuerpo["rentabilidad_maxima"] == 14.0
        assert cuerpo["hay_empate"] is False
        assert cuerpo["stock_por_producto"]["IRON"] == -2

    def test_conjunto_vacio_devuelve_ceros_y_ningun_mas_rentable(self):
        respuesta = enviar([])

        assert respuesta.status_code == status.HTTP_200_OK
        cuerpo = respuesta.json()
        assert set(cuerpo["stock_por_producto"].values()) == {0}
        assert cuerpo["productos_mas_rentables"] == []
        assert cuerpo["rentabilidad_maxima"] is None
        assert cuerpo["hay_empate"] is False

    def test_valor_unitario_decimal_se_calcula_con_precision(self):
        respuesta = enviar(
            [con_cambio(tipo="SELL", producto="GOLD", cantidad=3, valor_unitario="0.10")]
        )

        assert respuesta.json()["rentabilidad_por_producto"]["GOLD"] == 0.3


class TestErroresDeValidacion:
    @pytest.mark.parametrize(
        ("transaccion", "campo", "fragmento_del_mensaje"),
        [
            (con_cambio(tipo="TRADE"), "transacciones.0.tipo", "BUY"),
            (con_cambio(producto="SILVER"), "transacciones.0.producto", "COAL"),
            (con_cambio(cantidad=-5), "transacciones.0.cantidad", "mayor que 0"),
            (con_cambio(cantidad=0), "transacciones.0.cantidad", "mayor que 0"),
            (con_cambio(cantidad=1.5), "transacciones.0.cantidad", "entero"),
            (con_cambio(valor_unitario=-1), "transacciones.0.valor_unitario", "mayor que 0"),
            (con_cambio(valor_unitario="abc"), "transacciones.0.valor_unitario", "número"),
            (con_cambio(fecha="no-es-fecha"), "transacciones.0.fecha", "AAAA-MM-DD"),
            (con_cambio(color="rojo"), "transacciones.0.color", "no reconocido"),
        ],
    )
    def test_entrada_invalida_responde_422_con_el_campo_y_el_motivo(
        self, transaccion, campo, fragmento_del_mensaje
    ):
        respuesta = enviar([transaccion])

        assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        detalle = respuesta.json()["detalle"]
        assert detalle[0]["campo"] == campo
        assert fragmento_del_mensaje in detalle[0]["mensaje"]

    def test_campo_faltante_se_reporta_como_obligatorio(self):
        transaccion = {k: v for k, v in TRANSACCION_VALIDA.items() if k != "tipo"}

        respuesta = enviar([transaccion])

        assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert respuesta.json()["detalle"] == [
            {"campo": "transacciones.0.tipo", "mensaje": "Campo obligatorio."}
        ]

    def test_cuerpo_sin_la_lista_de_transacciones_responde_422(self):
        respuesta = CLIENTE.post(RUTA_ANALISIS, json={})

        assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert respuesta.json()["detalle"][0]["campo"] == "transacciones"

    def test_json_mal_formado_responde_422(self):
        respuesta = CLIENTE.post(
            RUTA_ANALISIS, content="{no es json", headers={"Content-Type": "application/json"}
        )

        assert respuesta.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert respuesta.json()["detalle"][0]["mensaje"] == "El cuerpo no es un JSON válido."

    def test_varios_errores_se_reportan_todos(self):
        respuesta = enviar([con_cambio(cantidad=-1, tipo="TRADE")])

        campos = {problema["campo"] for problema in respuesta.json()["detalle"]}
        assert campos == {"transacciones.0.cantidad", "transacciones.0.tipo"}


class TestDocumentacion:
    def test_api_docs_esta_disponible(self):
        assert CLIENTE.get(RUTA_DOCUMENTACION).status_code == status.HTTP_200_OK

    def test_openapi_documenta_los_codigos_200_y_422_del_endpoint(self):
        especificacion = CLIENTE.get("/openapi.json").json()

        operacion = especificacion["paths"][RUTA_ANALISIS]["post"]
        assert {"200", "422"} <= set(operacion["responses"])
        assert operacion["summary"]
        assert operacion["description"]
