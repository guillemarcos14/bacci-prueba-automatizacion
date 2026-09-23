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
