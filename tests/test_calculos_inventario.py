"""Pruebas unitarias de los cálculos de stock y rentabilidad (con valores calculados a mano)."""

from decimal import Decimal

from app.calculos.inventario import (
    calcular_rentabilidad_por_producto,
    calcular_stock_por_producto,
    identificar_productos_mas_rentables,
)
from app.enumeraciones import Producto, TipoTransaccion
from tests.fabricas import crear_transaccion, crear_transacciones_de_ejemplo


class TestStockPorProducto:
    def test_conjunto_vacio_deja_los_cinco_productos_en_cero(self):
        assert calcular_stock_por_producto([]) == {
            Producto.COAL: 0,
            Producto.GOLD: 0,
            Producto.IRON: 0,
            Producto.TIMBER: 0,
            Producto.ALUMINIUM: 0,
        }

    def test_ejemplo_completo_suma_compras_y_resta_ventas(self):
        stock = calcular_stock_por_producto(crear_transacciones_de_ejemplo())

        assert stock == {
            Producto.COAL: 70,
            Producto.GOLD: 15,
            Producto.IRON: -10,
            Producto.TIMBER: 0,
            Producto.ALUMINIUM: 0,
        }

    def test_producto_sin_transacciones_queda_en_cero(self):
        transacciones = [crear_transaccion(TipoTransaccion.BUY, Producto.GOLD, 7, 10)]

        stock = calcular_stock_por_producto(transacciones)

        assert stock[Producto.TIMBER] == 0
        assert stock[Producto.GOLD] == 7

    def test_ventas_mayores_que_compras_dejan_stock_negativo(self):
        transacciones = [
            crear_transaccion(TipoTransaccion.BUY, Producto.IRON, 5, 10),
            crear_transaccion(TipoTransaccion.SELL, Producto.IRON, 12, 10),
        ]

        assert calcular_stock_por_producto(transacciones)[Producto.IRON] == -7

    def test_varias_compras_del_mismo_producto_se_acumulan(self):
        transacciones = [
            crear_transaccion(TipoTransaccion.BUY, Producto.COAL, 10, 1),
            crear_transaccion(TipoTransaccion.BUY, Producto.COAL, 15, 1),
            crear_transaccion(TipoTransaccion.SELL, Producto.COAL, 5, 1),
        ]

        assert calcular_stock_por_producto(transacciones)[Producto.COAL] == 20


class TestRentabilidadPorProducto:
    def test_conjunto_vacio_deja_rentabilidad_en_cero(self):
        rentabilidad = calcular_rentabilidad_por_producto([])

        assert set(rentabilidad.values()) == {Decimal(0)}
        assert set(rentabilidad) == set(Producto)

    def test_ejemplo_completo_solo_cuenta_las_ventas(self):
        rentabilidad = calcular_rentabilidad_por_producto(crear_transacciones_de_ejemplo())

        assert rentabilidad == {
            Producto.COAL: Decimal(1500),
            Producto.GOLD: Decimal(1500),
            Producto.IRON: Decimal(1000),
            Producto.TIMBER: Decimal(0),
            Producto.ALUMINIUM: Decimal(0),
        }

    def test_las_compras_no_generan_rentabilidad(self):
        transacciones = [crear_transaccion(TipoTransaccion.BUY, Producto.GOLD, 100, 999)]

        assert calcular_rentabilidad_por_producto(transacciones)[Producto.GOLD] == Decimal(0)

    def test_varias_ventas_se_suman(self):
        transacciones = [
            crear_transaccion(TipoTransaccion.SELL, Producto.TIMBER, 2, 10),
            crear_transaccion(TipoTransaccion.SELL, Producto.TIMBER, 3, 20),
        ]

        assert calcular_rentabilidad_por_producto(transacciones)[Producto.TIMBER] == Decimal(80)

    def test_valores_unitarios_decimales_no_pierden_precision(self):
        transaccion = crear_transaccion(TipoTransaccion.SELL, Producto.COAL, 3, 1)
        transaccion_decimal = type(transaccion)(
            tipo=transaccion.tipo,
            fecha=transaccion.fecha,
            producto=transaccion.producto,
            cantidad=3,
            valor_unitario=Decimal("0.10"),
        )

        rentabilidad = calcular_rentabilidad_por_producto([transaccion_decimal])

        assert rentabilidad[Producto.COAL] == Decimal("0.30")


class TestProductosMasRentables:
    def test_un_solo_producto_mas_rentable(self):
        rentabilidad = calcular_rentabilidad_por_producto(
            [
                crear_transaccion(TipoTransaccion.SELL, Producto.IRON, 10, 100),
                crear_transaccion(TipoTransaccion.SELL, Producto.COAL, 1, 5),
            ]
        )

        resultado = identificar_productos_mas_rentables(rentabilidad)

        assert resultado.productos == (Producto.IRON,)
        assert resultado.rentabilidad == Decimal(1000)
        assert resultado.hay_empate is False

    def test_empate_devuelve_todos_los_productos_en_orden_alfabetico(self):
        rentabilidad = calcular_rentabilidad_por_producto(crear_transacciones_de_ejemplo())

        resultado = identificar_productos_mas_rentables(rentabilidad)

        assert resultado.productos == (Producto.COAL, Producto.GOLD)
        assert resultado.rentabilidad == Decimal(1500)
        assert resultado.hay_empate is True

    def test_sin_ventas_no_hay_producto_mas_rentable(self):
        rentabilidad = calcular_rentabilidad_por_producto([])

        resultado = identificar_productos_mas_rentables(rentabilidad)

        assert resultado.productos == ()
        assert resultado.rentabilidad is None
        assert resultado.hay_empate is False

    def test_solo_compras_tampoco_genera_producto_mas_rentable(self):
        rentabilidad = calcular_rentabilidad_por_producto(
            [crear_transaccion(TipoTransaccion.BUY, Producto.GOLD, 10, 10)]
        )

        assert identificar_productos_mas_rentables(rentabilidad).productos == ()
