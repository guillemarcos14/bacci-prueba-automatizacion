# Prioridad, estado y etiqueta del caso

Las tres nociones son distintas. **Prioridad** (`Alta`, `Media`, `Baja`) ordena exclusivamente los casos activos. **Estado operativo** distingue un caso activo de una línea `Servido`. La **etiqueta del caso seleccionado** resume qué debe interpretar primero quien lo revisa; no sustituye el motivo, la acción ni la evidencia.

## Qué entra en la cola

Una línea entra si sus unidades pendientes son desconocidas o mayores que cero, o si existe cancelación, petición de fecha, anomalía de origen o consulta de seguimiento. Un duplicado idéntico consolidado, por sí solo, no es anomalía. Una línea con cero pendientes y sin esas señales es `Servido`: se consulta en «Todos los registros» y no entra en la cola. Los correos sin vínculo fiable son casos activos `Sin correspondencia`, incluidos en la cola y en «Sin resolver».

## Regla exacta de prioridad

Se aplica la **primera** condición verdadera de esta tabla, de arriba abajo. «Hoy» es el día del corte en `Europe/Madrid` (10/09/2026 en esta prueba). Una petición de correo nunca modifica la fecha del ERP.

| Orden | Condición | Prioridad | Rango |
| ---: | --- | --- | ---: |
| 1 | Solicitud de cancelación | Alta | 0 |
| 2 | Fecha solicitada vigente para hoy o antes | Alta | 1 |
| 3 | Contacto nuevo o remitente no coincidente por verificar | Alta | 2 |
| 4 | Anomalía y pendiente desconocido | Alta | 3 |
| 5 | Pendiente positivo y compromiso ERP anterior a hoy | Alta | 4 |
| 6 | Pendiente positivo y compromiso ERP para hoy | Alta | 5 |
| 7 | Petición de cambio de fecha vigente | Media | 10 |
| 8 | Anomalía de origen o peticiones activas incompatibles | Media | 11 |
| 9 | Pendiente positivo y compromiso en los próximos dos días | Media | 12 |
| 10 | Consulta de seguimiento | Media | 13 |
| 11 | Ninguna condición anterior | Baja | 20 |

La anomalía abarca filas contradictorias, cantidades inválidas o sobreexpedidas, fecha de compromiso desconocida, cliente ausente del maestro, contacto por verificar y varias peticiones sin rectificación explícita. Una fecha vacía es desconocida; no se considera vencida. Entre casos del mismo rango se ordena primero la fecha ERP conocida más temprana, después el correo más reciente y por último el identificador estable. El motivo y la acción siguen esta misma precedencia; `Servido` muestra «Línea servida sin incidencia» y ninguna acción.

Los correos sin correspondencia que solicitan cancelación o cambio de fecha son `Alta` con rango 2. El resto son `Media` con rango 13. Su acción siempre es investigar la referencia y asociarla únicamente tras verificación humana.

## Etiqueta del caso seleccionado

También se usa la **primera** condición verdadera. Por eso una etiqueta puede ser «Revisión humana» aunque la prioridad sea `Alta`, o «Solicitud sin confirmar» aunque el motivo sea urgente. La prioridad sigue visible en la tabla.

| Orden | Condición | Etiqueta |
| ---: | --- | --- |
| 1 | Línea sin trabajo activo | **Servido** |
| 2 | Correo sin correspondencia fiable | **Sin correspondencia** |
| 3 | Línea con cualquier anomalía indicada arriba | **Revisión humana** |
| 4 | Línea con petición vigente de cambio de fecha, incluso si no se pudo extraer fecha | **Solicitud sin confirmar** |
| 5 | Caso activo de prioridad `Alta` | **Atención prioritaria** |
| 6 | Cualquier otro caso activo | **Pendiente** |

«Pendiente» en esta etiqueta significa trabajo abierto; puede tener prioridad `Media` o `Baja`. «Solicitud sin confirmar» expresa que el correo pide un cambio y falta validar su viabilidad. «Atención prioritaria» identifica los casos `Alta` que no quedaron descritos por una condición anterior. «Revisión humana» exige contrastar el dato o la identidad; no significa que el ERP haya cambiado. Las líneas servidas no heredan la prioridad interna `Baja` en la búsqueda o la interfaz.

Operaciones verifica stock, expedición, capacidad logística e identidad antes de prometer una fecha, cancelar o cambiar Navision. El prototipo propone la acción y conserva las filas y mensajes que la justifican.
