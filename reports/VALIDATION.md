# Validación ejecutada · 23/09/2026

Fuente reproducible: `python tools/harness.py --dataset both --output reports/validation.json`. El JSON conserva los 76 oráculos con valor esperado y obtenido, hashes y tiempos exactos. Resultado: **76/76 comprobaciones conformes**.

| Conjunto | Etapa | Mensajes nuevos | Reentregas ignoradas | Mensajes activos | Casos | Sin resolver | Tiempo |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Muestra | Inicial, 10:00 | 24 | 1 | 24 | 90 | 2 | 113,14 ms |
| Muestra | Actualización, 11:00 | 3 | 2 | 27 | 90 | 2 | 85,62 ms |
| Muestra | Repetición, 11:00 | 0 | 5 | 27 | 90 | 2 | 89,18 ms |
| Completo | Inicial, 10:00 | 3.800 | 200 | 3.800 | 17.423 | 569 | 12.746,66 ms |
| Completo | Actualización, 11:00 | 3 | 2 | 3.803 | 17.423 | 569 | 13.213,12 ms |
| Completo | Repetición, 11:00 | 0 | 5 | 3.803 | 17.423 | 569 | 14.167,73 ms |

La muestra cambia de digest `cb93c0f21c97` a `c06cc19a22e9` con el lote; repetirlo conserva `c06cc19a22e9`. El conjunto completo cambia de `0426cffa61ff` a `3c7a0941103e` y lo conserva al repetir.

El historial de cambios registra **2 casos afectados** en la actualización y **0** al repetir, en ambos tamaños. P-26002 muestra la petición vigente **12/09 → 13/09** y dos correos vinculados adicionales; P-26004 muestra un seguimiento adicional. El filtro **Revisión humana** devuelve **7** casos en muestra y **767** en completo. En el conjunto completo, **43 líneas** contienen fechas solicitadas activas incompatibles: P-30168 muestra 21/09 y 24/09 sin elegir una por orden de llegada. El arnés recorrió todos los registros para comprobar aritmética en líneas sin duplicados, procedencia de pedidos y correos y coherencia de etiquetas. Se comprobó en navegador la combinación del filtro, la apertura del antes/después y el enlace al caso actual, en escritorio y móvil, sin desbordamiento horizontal de la página. La API local activa en el puerto 8765 devuelve 767 casos filtrados y dos cambios para la carga de actualización.

En el conjunto completo actualizado, las etiquetas del detalle se distribuyen así: **Atención prioritaria 6.914**, **Pendiente 8.118**, **Revisión humana 767**, **Solicitud sin confirmar 1.055**, **Sin correspondencia 569** y **Servido 2.546**. Suman los 19.969 registros; las cinco primeras categorías corresponden a los 17.423 casos activos. La regla y precedencia se detallan en `docs/PRIORITY.md`.

La batería unitaria incluye 8 pruebas, con subcasos de búsqueda sobre prioridad, estado, pedidos, líneas, SKU, color, talla, cantidades, fechas ISO y locales, correos, maestro de clientes, tildes, mayúsculas, términos combinados y filtros simultáneos. Comprueba además la fila física de pedidos y correos, el cálculo visible, la recuperación de procedencia en una base anterior y la conservación de fechas incompatibles. En la API local, `baja` devolvió 7.060 casos activos y `servido` 2.546 líneas servidas; `/api/health` respondió correctamente. La tabla se revisó en escritorio, tableta y móvil; las filas de «Revisión humana» conservaron la altura de «Todos» en los anchos probados.

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
