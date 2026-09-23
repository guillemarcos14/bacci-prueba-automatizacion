# Decisiones

| Fecha | Decisión | Motivo |
| --- | --- | --- |
| 23/09/2026 | Python, `openpyxl`, SQLite y servidor HTTP local de la biblioteca estándar | Una instalación pequeña y un proceso trazable para 20.000 líneas y 4.000 correos. |
| 23/09/2026 | Recalcular casos después de cada lote; persistir mensajes por ID | Hace simple la actualización y permite demostrar idempotencia sin editar filas. |
| 23/09/2026 | Consolidar duplicados idénticos; dejar pendiente desconocido si la cantidad es contradictoria o hay sobreexpedición | No existe versión ni orden de prevalencia en el ERP exportado. |
| 23/09/2026 | Usar reglas deterministas de extracción y mostrar ambiguos sin resolver | Facilita explicar cada cruce y evita asignaciones inventadas. |
| 23/09/2026 | Correo como evidencia y solicitud, nunca como cambio confirmado de fecha | El diccionario lo exige y no hay datos de viabilidad logística. |
| 23/09/2026 | Prioridad legible con suborden de cancelación, adelanto para hoy, identidad/datos dudosos y vencimiento | Facilita actuar primero sobre decisiones urgentes; el criterio está en `docs/PRIORITY.md`. |
| 23/09/2026 | Mantener el fondo y la paleta de la referencia ERP/POS, pero sustituir sus secciones por trabajo real de Bacci | Dirección visual aprobada por Guillem. |
| 23/09/2026 | Extender el fondo degradado a toda la ventana y aprovechar el ancho disponible | Corrección visual solicitada tras revisar la primera versión. |
| 23/09/2026 | Selector de muestra y conjunto completo dentro de la app, con bases separadas | Hace visible el alcance real sin pedir que operaciones reinicie el servidor. |
| 23/09/2026 | Guardar líneas servidas como registros consultables, fuera de la cola operativa | La cola sigue enfocada en acciones, mientras la búsqueda puede encontrar cualquier línea importada. |
| 23/09/2026 | Indexar valores de pedido, maestro y correos sin tildes ni distinción de mayúsculas | Permite buscar SKU, fechas, unidades, direcciones y texto, además de pedido o cliente. |
