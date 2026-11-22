"""Pruebas unitarias de la traducción de errores de validación."""

from app.errores import mensaje_en_espanol, nombre_del_campo


class TestNombreDelCampo:
    def test_quita_el_prefijo_body_y_une_con_puntos(self):
        ubicacion = ("body", "transacciones", 0, "cantidad")

        assert nombre_del_campo(ubicacion) == "transacciones.0.cantidad"

    def test_ubicacion_solo_con_body_queda_vacia(self):
        assert nombre_del_campo(("body",)) == ""


class TestMensajeEnEspanol:
    def test_rellena_la_plantilla_con_el_contexto(self):
        error = {"type": "greater_than", "msg": "original", "ctx": {"gt": 0}}

        assert mensaje_en_espanol(error) == "Debe ser mayor que 0."

    def test_error_sin_contexto_usa_plantilla_fija(self):
        error = {"type": "missing", "msg": "original"}

        assert mensaje_en_espanol(error) == "Campo obligatorio."

    def test_tipo_sin_plantilla_devuelve_el_mensaje_original(self):
        error = {"type": "tipo_desconocido", "msg": "mensaje original"}

        assert mensaje_en_espanol(error) == "mensaje original"
