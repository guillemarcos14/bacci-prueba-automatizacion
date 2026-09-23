# Validación ejecutada · 23/09/2026

Fuente reproducible: `python tools/harness.py --dataset both --output reports/validation.json`. El JSON conserva los 40 oráculos con valor esperado y obtenido, hashes y tiempos exactos. Resultado: **40/40 comprobaciones conformes**.

| Conjunto | Etapa | Mensajes nuevos | Reentregas ignoradas | Mensajes activos | Casos | Sin resolver | Tiempo |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Muestra | Inicial, 10:00 | 24 | 1 | 24 | 90 | 2 | 89,59 ms |
| Muestra | Actualización, 11:00 | 3 | 2 | 27 | 90 | 2 | 64,22 ms |
| Muestra | Repetición, 11:00 | 0 | 5 | 27 | 90 | 2 | 63,72 ms |
| Completo | Inicial, 10:00 | 3.800 | 200 | 3.800 | 17.423 | 569 | 9.120,18 ms |
| Completo | Actualización, 11:00 | 3 | 2 | 3.803 | 17.423 | 569 | 8.588,22 ms |
| Completo | Repetición, 11:00 | 0 | 5 | 3.803 | 17.423 | 569 | 9.059,28 ms |

La muestra cambia de digest `3999816788cb` a `3349971f02e2` con el lote; repetirlo conserva `3349971f02e2`. El conjunto completo cambia de `b0e0fc7a0748` a `2e19baef16f0` y lo conserva al repetir.

## Casos contrastados

| Caso | Esperado | Obtenido |
| --- | --- | --- |
| P-26002 / 10000 | Petición vigente 12/09 inicialmente; 13/09 tras rectificación; acuse sin nuevo cambio | Conforme; 4 correos vinculados tras actualización |
| P-26004 / 10000 | 250 unidades pendientes y compromiso vencido | Conforme |
| P-26009 / 10000 | Dos filas contradictorias; pendiente desconocido | Conforme; no se eligió fila por posición |
| P-26003 / 10000 | Duplicado idéntico; 300 pendientes | Conforme |
| P-26008 / 10000 | Sobreexpedición; no mostrar pendiente negativo | Conforme |
| P-26001 / 20000 | Cancelación visible aunque hay 0 pendientes | Conforme |
| P-99999 / 10000 | Correo sin correspondencia ERP | Conforme en «Sin resolver» |

Los tiempos son mediciones locales de esta ejecución, no un compromiso de servicio. La prueba no aporta stock, capacidad logística ni verificación de contactos; la aplicación deja esas decisiones a operaciones.
