# Validación ejecutada · 23/09/2026

Fuente reproducible: `python tools/harness.py --dataset both --output reports/validation.json`. El JSON conserva los 50 oráculos con valor esperado y obtenido, hashes y tiempos exactos. Resultado: **50/50 comprobaciones conformes**.

| Conjunto | Etapa | Mensajes nuevos | Reentregas ignoradas | Mensajes activos | Casos | Sin resolver | Tiempo |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Muestra | Inicial, 10:00 | 24 | 1 | 24 | 90 | 2 | 101,19 ms |
| Muestra | Actualización, 11:00 | 3 | 2 | 27 | 90 | 2 | 77,42 ms |
| Muestra | Repetición, 11:00 | 0 | 5 | 27 | 90 | 2 | 80,96 ms |
| Completo | Inicial, 10:00 | 3.800 | 200 | 3.800 | 17.423 | 569 | 12.079,88 ms |
| Completo | Actualización, 11:00 | 3 | 2 | 3.803 | 17.423 | 569 | 11.917,71 ms |
| Completo | Repetición, 11:00 | 0 | 5 | 3.803 | 17.423 | 569 | 11.543,42 ms |

La muestra cambia de digest `b53b9748cbf5` a `3fa6a4e4027a` con el lote; repetirlo conserva `3fa6a4e4027a`. El conjunto completo cambia de `688c34267182` a `c8d455edc5c5` y lo conserva al repetir.

En el conjunto completo actualizado, las etiquetas del detalle se distribuyen así: **Atención prioritaria 6.914**, **Pendiente 8.118**, **Revisión humana 767**, **Solicitud sin confirmar 1.055**, **Sin correspondencia 569** y **Servido 2.546**. Suman los 19.969 registros; las cinco primeras categorías corresponden a los 17.423 casos activos. La regla y precedencia se detallan en `docs/PRIORITY.md`.

La batería unitaria incluye 7 pruebas, con subcasos de búsqueda sobre prioridad, estado, pedidos, líneas, SKU, color, talla, cantidades, fechas ISO y locales, correos, maestro de clientes, tildes, mayúsculas, términos combinados y filtros simultáneos. Comprueba además la fila física de pedidos y correos, el cálculo visible y la recuperación de procedencia en una base anterior. En la API local, `baja` devolvió 7.060 casos activos y `servido` 2.546 líneas servidas; `/api/health` respondió correctamente. La tabla de escritorio se comprobó a 1.002 px: margen exterior 25,05 px, radios de cabecera y fila seleccionada de 8 px y texto completo en cliente y acción.

## Casos contrastados

| Caso | Esperado | Obtenido |
| --- | --- | --- |
| P-26002 / 10000 | Petición vigente 12/09 inicialmente; 13/09 tras rectificación; acuse sin nuevo cambio | Conforme; 4 correos vinculados tras actualización |
| P-26004 / 10000 | 250 unidades pendientes y compromiso vencido | Conforme |
| P-26009 / 10000 | Dos filas contradictorias; pendiente desconocido | Conforme; filas 11.164 y 18.936 visibles, sin elegir una por posición |
| P-26003 / 10000 | Duplicado idéntico; 300 pendientes | Conforme; filas 7.248 y 12.350 conservadas |
| P-26008 / 10000 | Sobreexpedición; no mostrar pendiente negativo | Conforme |
| P-26001 / 20000 | Cancelación visible aunque hay 0 pendientes | Conforme |
| P-99999 / 10000 | Correo sin correspondencia ERP | Conforme en «Sin resolver» |

Los tiempos son mediciones locales de esta ejecución, no un compromiso de servicio. La prueba no aporta stock, capacidad logística ni verificación de contactos; la aplicación deja esas decisiones a operaciones.
