# Auditoría de la iteración · 23/09/2026

## Resultado verificado

Se revisaron motor de ingesta y clasificación, base SQLite, API local, interfaz de escritorio, búsqueda, textos y documentación contra el enunciado y los XLSX originales. La cola mantiene 17.423 casos activos, de ellos 569 sin correspondencia; «Todos los registros» contiene 19.969 registros, incluidas 2.546 líneas servidas. El arnés conserva 20/20 oráculos en muestra y 20/20 en completo, y la repetición del lote no altera el resultado. No se modificaron los XLSX, el PDF, el diccionario ni el vídeo.

## Hallazgos corregidos

1. **P1 · Estado confundido con prioridad.** El índice contenía `Baja` en líneas servidas por su prioridad interna. La búsqueda exacta de `baja` ahora exige caso activo y esa prioridad; `servido` exige línea inactiva. Los términos se combinan con AND y con cliente/prioridad seleccionados.
2. **P1 · Etiqueta y motivo con precedencias dispersas.** La etiqueta vivía solo en JavaScript y algunas acciones no seguían el mismo orden que la prioridad. El motor calcula la etiqueta con seis categorías y una única precedencia; el motivo y la acción siguen el orden de prioridad. La tabla exacta está en `docs/PRIORITY.md`.
3. **P2 · Acción y cliente truncados en la tabla de escritorio.** Las celdas relevantes ahora envuelven el texto y la columna de acción recibe más ancho. El detalle conserva la evidencia completa.
4. **P2 · Margen y cabecera.** El lienzo aumenta el margen de los cuatro bordes sin fijar un ancho máximo. La cabecera pasa de radio de píldora a 8 px, igual al extremo de la fila seleccionada.
5. **P2 · Rótulo ambiguo en fichas compactas.** «Pendiente» en la cantidad pasó a «Por servir», para distinguir unidades de la etiqueta de caso.

## Mejores siguientes pasos, fuera de esta iteración

1. **P1 · Registro de decisiones humanas.** Añadir resolución, responsable y marca temporal por caso tras definir permisos y sistema de referencia. Hoy la acción es sugerida y no queda constancia de su ejecución.
2. **P1 · Reconciliación entre exportaciones ERP.** Registrar versión o corte de cada archivo y comparar líneas cambiadas antes de sustituir el estado. Los XLSX de prueba no ofrecen historial fiable de movimientos.
3. **P2 · Navegación de una cola extensa.** Incorporar enlaces a casos concretos y tamaños de página opcionales; 17.423 casos en páginas de seis requieren buscar o filtrar para saltar lejos.
4. **P2 · Índice de texto especializado si crece el volumen.** Medir consultas sobre archivos reales de operación y considerar FTS de SQLite; el prototipo usa `LIKE` sobre 19.969 registros y no promete un tiempo de búsqueda de producción.

Las conexiones reales, stock, capacidad logística, autorización de contactos y el vídeo final siguen sujetos a las fuentes y decisiones de Bacci. Esta auditoría no los simula ni afirma haberlos validado.

## Cierre funcional posterior · 23/09/2026

En esa iteración, el detalle pasó a exponer pedidas, enviadas acumuladas y pendientes junto a cada fila original del ERP (archivo, hoja y fila). Los correos mostraron la primera fila de origen, remitente, destinatario y texto completo. La migración recuperó la procedencia de mensajes ya almacenados contrastando su huella. Entonces pasaban 25/25 oráculos por conjunto y 7 pruebas unitarias; `reports/VALIDATION.md` recoge la evidencia más reciente. El vídeo final continúa pendiente.

## Impacto y revisión humana · 23/09/2026

Las dos mejoras operativas propuestas están implementadas: Control de cargas compara los casos de cada ejecución y la cola filtra «Revisión humana». El navegador verificó ambos flujos en escritorio y móvil; `reports/VALIDATION.md` contiene la evidencia actual. El vídeo final permanece pendiente de la presentación.

## Auditoría global previa al fork final · 23/09/2026

Se recorrieron los menús, filtros, búsqueda, tabla, detalle, evidencia, actualización, repetición, navegación con teclado, estados vacíos y rutas de error en escritorio, tableta y móvil. Se detectó un fallo funcional: ante dos fechas solicitadas activas sin rectificación, la aplicación mostraba la última como única vigente. Ahora conserva y muestra todas, exige aclaración y mantiene la urgencia de cualquiera que venza hoy o antes. El arnés pasa 38/38 oráculos por tamaño, incluida la verificación global de aritmética, procedencia y etiquetas; pasan 8 pruebas unitarias. Se actualizaron las capturas del README. El fork y el vídeo final todavía deben cerrarse.
