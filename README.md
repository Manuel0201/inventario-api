# API de Inventario: stock y rentabilidad

API REST en Python (FastAPI) que recibe transacciones de compra (`BUY`) y venta (`SELL`) de cinco
productos (`COAL`, `GOLD`, `IRON`, `TIMBER`, `ALUMINIUM`) y devuelve:

- el **stock final** por producto (BUY suma, SELL resta; puede ser negativo),
- la **rentabilidad** por producto (suma de cantidad × valor unitario solo de las SELL),
- el/los **producto(s) más rentable(s)**, con detalle si hay empate.

## Decisiones de diseño

| Decisión | Elección | Por qué |
|----------|----------|---------|
| Formato de entrada | JSON en el body | Simple, validable con Pydantic y probable desde `/api-docs`. |
| Persistencia | Ninguna: se calcula al vuelo | El enunciado la deja opcional; la API es una función pura de la entrada, sin estado. Por eso no se usa base de datos. |
| Empates | Se devuelven todos los empatados | Más fiel a los datos; `hay_empate` y `rentabilidad_por_producto` dan el detalle. |
| Sin ventas | `productos_mas_rentables: []` y `rentabilidad_maxima: null` | No existe un "más rentable" si nadie vendió. |

Stack: Python 3.12+, FastAPI (endpoints síncronos), Pydantic 2. Arquitectura en tres capas:
`routers` (solo declaran la ruta) → `servicios` (coordinan) → `calculos` (funciones puras).

## Cómo correrlo

```bash
python -m venv .venv
.venv\Scripts\activate            # en Linux/Mac: source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

- Documentación OpenAPI interactiva: <http://localhost:8000/api-docs>
- No requiere base de datos ni variables de entorno.

## Endpoint

`POST /inventario/analisis`

Petición:

```json
{
  "transacciones": [
    {"tipo": "BUY",  "fecha": "2020-05-05", "producto": "COAL", "cantidad": 100, "valor_unitario": 10},
    {"tipo": "SELL", "fecha": "2020-05-05", "producto": "COAL", "cantidad": 30,  "valor_unitario": 50},
    {"tipo": "BUY",  "fecha": "2020-05-05", "producto": "GOLD", "cantidad": 20,  "valor_unitario": 200},
    {"tipo": "SELL", "fecha": "2020-05-05", "producto": "GOLD", "cantidad": 5,   "valor_unitario": 300},
    {"tipo": "SELL", "fecha": "2020-05-05", "producto": "IRON", "cantidad": 10,  "valor_unitario": 100}
  ]
}
```

Respuesta `200`:

```json
{
  "stock_por_producto": {"COAL": 70, "GOLD": 15, "IRON": -10, "TIMBER": 0, "ALUMINIUM": 0},
  "rentabilidad_por_producto": {"COAL": 1500.0, "GOLD": 1500.0, "IRON": 1000.0, "TIMBER": 0.0, "ALUMINIUM": 0.0},
  "productos_mas_rentables": ["COAL", "GOLD"],
  "rentabilidad_maxima": 1500.0,
  "hay_empate": true
}
```

Una lista vacía de transacciones es válida: todos los stocks quedan en 0 y no hay producto más
rentable.

### Errores

Cualquier entrada inválida responde `422` con el campo y el motivo:

```json
{"detalle": [{"campo": "transacciones.0.cantidad", "mensaje": "Debe ser mayor que 0."}]}
```

Se rechazan: tipo distinto de `BUY`/`SELL`, producto no reconocido, `cantidad` no entera o ≤ 0,
`valor_unitario` ≤ 0 o no numérico, fecha con formato inválido, campos faltantes o desconocidos y
JSON mal formado.

## Pruebas y calidad

```bash
pytest          # corre las pruebas y exige cobertura mínima del 80 %
ruff check .    # linter
ruff format .   # formato
```

- Pruebas unitarias de los cálculos con valores calculados a mano y casos borde: conjunto vacío,
  producto sin transacciones, stock negativo, empate y ausencia de ventas.
- Pruebas de integración del endpoint que validan el contrato de respuesta, los errores `422` y la
  documentación OpenAPI.
- Cobertura actual: 100 %.

## Notas

- El dinero se calcula con `Decimal` (sin errores de punto flotante) y se entrega en el JSON como número.
- El orden de los empatados es alfabético, para que la respuesta sea siempre la misma.
