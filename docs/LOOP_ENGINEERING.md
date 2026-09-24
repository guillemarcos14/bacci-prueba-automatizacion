# Loop de ingeniería y operación

El ciclo del prototipo es `archivo → validación de estructura → deduplicación → cruce → clasificación → caso → evidencia → revisión humana → nueva ejecución`.

## Invariantes

1. La fuente ERP es un estado al corte, no un historial de movimientos. Una línea conserva una sola identidad compuesta y sus filas originales.
2. El mensaje se conserva por `message_id`. Una reentrega idéntica no cambia casos; mismo ID con distinto contenido se cuenta como conflicto y no sobrescribe.
3. Las rectificaciones con referencia explícita sustituyen la petición anterior. Un acuse no produce petición nueva. Ningún correo modifica el ERP.
4. Un cruce sin pedido/línea verificable crea un caso sin resolver. Sugerencias por SKU nunca se aplican automáticamente.
5. El corte determina qué correos participan; la nueva ejecución es reproducible y deja hash, recuentos y tiempo.

## Paso humano

Operaciones verifica stock, expedición, capacidad logística y autorización del contacto antes de prometer una fecha, cancelar una línea o actualizar Navision. La aplicación propone el siguiente paso y conserva la evidencia; no ejecuta acciones externas.

## Cierre del ciclo

`tools/harness.py` compara resultados esperados y obtenidos, y repite el lote. Un fallo detiene el cierre de la tarea. Si un caso revela una regla nueva, añadir primero una comprobación específica, corregir el motor y registrar la decisión y el aprendizaje.
