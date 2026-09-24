# Estado actual

**24/09/2026.** El prototipo local está terminado y publicado en el fork. Incluye conciliación de pedidos y correos, base SQLite, CLI, API local e interfaz operativa. Pasan 8 pruebas unitarias y 38 comprobaciones del arnés en cada conjunto; los resultados están en `reports/validation.json`. El README explica cómo ejecutarlo, qué resultados produce y cuáles son sus límites. El vídeo final está publicado como `demo-v5` y enlazado desde el README.

La aplicación no accede a Navision ni Outlook reales y no envía correos. Las decisiones que requieren stock, logística o verificación de identidad quedan para una persona.

## Historial de trabajo

**Iteración intermedia, 23/09/2026 (sustituida).** Fondo extendido a toda la pantalla; búsqueda sobre los valores importados; selector de muestra/completo; vista de todos los registros, incluidas líneas servidas. Validación repetida con 20/20 comprobaciones por conjunto y pruebas de interfaz en escritorio y móvil. La cola mantenía 90 casos en muestra y 17.423 en completo; la vista de registros mostraba 100 y 19.969, respectivamente.

**Revisión posterior, 23/09/2026.** La interfaz y el servidor quedan fijados al conjunto completo; no existe selector ni subtítulo de volumen. «Prioridad alta» pasa a ser el filtro `Prioridad → Alta`, y «Sin resolver» tiene una única entrada en el menú lateral. «Ejecuciones» se llama ahora «Control de cargas». El correo `msg-13756` se ha contrastado con los XLSX originales y su procedencia consta en `docs/SOURCES.md`. La muestra permanece disponible únicamente para CLI y validación.

La aplicación usa `data/operations.sqlite` para mantener su historial de cargas separado de los ensayos por CLI. El historial visible se inicializó limpiamente desde los XLSX originales; los ensayos previos en `data/full.sqlite` se conservaron localmente.

**Revisión de comprensión, 23/09/2026.** Retirados los dos textos de marco solicitados. Control de cargas define sus tres contadores por lote. El filtro de prioridad se limita a casos activos para excluir «Servido». Se deja el vídeo `demo-v4` como material de la iteración anterior; se grabará uno final cuando la plataforma quede cerrada.

**Revisión de escritorio y semántica, 23/09/2026.** Márgenes ampliados, radio de cabecera igualado a la fila seleccionada y acciones completas visibles en tabla. Búsqueda de prioridad y estado separada, palabras combinables con datos de origen, tildes y fechas. Etiquetas del detalle centralizadas en el motor y documentadas con precedencia exacta. Auditoría y propuestas en `docs/AUDIT.md`. El vídeo anterior permanece intacto; no se genera ni publica otro en esta iteración.

**Ajuste de marca y separación, 23/09/2026.** La marca lateral muestra «Bacci» y «Operations» con el mismo formato, cada uno en una línea. La barra de vistas queda a 8 px de la tarjeta blanca. Comprobado en escritorio; el usuario prioriza esta versión y el enunciado no exige móvil.

**Cierre funcional de trazabilidad, 23/09/2026.** El detalle visible incorpora unidades pedidas, enviadas acumuladas y pendientes, filas originales del ERP con archivo/hoja/fila, y la primera ubicación física de cada correo con remitente, destinatario y texto. Las bases anteriores recuperan la procedencia del correo sin cambiar su contenido. Verificado en escritorio y móvil, sin desbordamiento; 7 pruebas unitarias y 50/50 comprobaciones del arnés con muestra y completo. El vídeo final seguía pendiente entonces.

**Impacto entre cortes y revisión humana, 23/09/2026.** Control de cargas muestra los casos afectados por cada ejecución con valores antes/después y apertura del caso actual. La cola filtra «Revisión humana» junto a cliente, prioridad y búsqueda. La actualización cambia dos casos; repetirla, cero. La base anterior a esta función se conserva localmente en `data/operations-before-impact.sqlite`.

**Auditoría global previa a la entrega, 23/09/2026.** Detectada y corregida la elección indebida de la última fecha en 43 líneas con solicitudes incompatibles. La ficha muestra todas las fechas y exige aclaración; cualquier solicitud urgente sigue priorizada. Verificados los cuatro menús/vistas, filtros, búsqueda, paginación, navegación con teclado, detalles, procedencia, actualización y repetición en navegador, escritorio, tableta y móvil. Pasaron 8 pruebas unitarias y 76/76 comprobaciones, incluidas reglas revisadas sobre todos los registros. `data/operations.sqlite` se reconstruyó con los dos cortes limpios; el historial local anterior se conserva en `data/operations-before-date-audit.sqlite`. Se actualizaron las capturas del README. En ese momento quedaban pendientes la subida al fork y el vídeo final.

**Vídeo final de entrega, 24/09/2026.** `Demo_Bacci.mp4` (205 MB) se adjuntó a la release pública `demo-v5` del fork. Su descarga devuelve HTTP 200. El README enlaza el vídeo final dirigido al equipo de Bacci; el vídeo previo `demo-v4` se conserva como referencia.
