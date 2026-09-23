# Aprendizajes verificados

- La muestra tiene 100 filas de pedidos, 98 líneas únicas, una duplicación idéntica y otra contradictoria. El conjunto completo tiene 20.000 filas y 19.400 líneas únicas.
- La muestra inicial trae 25 filas de correo y 24 `message_id` únicos. El conjunto completo trae 4.000 filas y 3.800 ID únicos. El lote de actualización añade tres mensajes y contiene dos reentregas; su segunda ejecución añade cero.
- P-26002 demuestra que una rectificación posterior cambia la **petición vigente** de 12/09 a 13/09; el acuse posterior no crea otra fecha ni cambia el ERP.
- Una fecha `dd/mm/aaaa` contiene barras; el analizador no puede tratar `/2026` como si fuera `linea_id`. Una prueba cubre este fallo y la línea de P-33853.
- Los casos sin referencia fiable tienen valor operativo si permanecen en una cola visible con el correo original y una acción de investigación.
- Los 90 casos de la primera versión procedían de la muestra: 88 líneas con trabajo y 2 correos sin resolver. No eran un límite de cálculo. La aplicación actual abre siempre el conjunto completo, con 17.423 casos.
- Las 98 líneas únicas de la muestra siguen consultables; diez están servidas y fuera de la cola. Con los dos correos sin resolver, **Todos los registros** muestra 100. En el conjunto completo muestra 19.969: 19.400 líneas únicas y 569 correos sin resolver.
- `msg-13756` es una fila original de `Correos_full.xlsx` (fila 2622), no un ejemplo añadido a mano. La referencia `P-X003756` no existe en los pedidos entregados, por lo que la acción segura es investigarla. Las prioridades y acciones son derivaciones del motor, distintas del texto fuente.
- En el conjunto completo, la cola son 16.854 líneas activas y 569 correos sin resolver; Todos los registros añade 2.546 líneas servidas. «Sin resolver» es subconjunto de ambos. El filtro Baja no debe incluir líneas «Servido».
- El filtro de prioridad no bastaba: el índice de búsqueda aún incluía la prioridad interna `Baja` de líneas servidas. La búsqueda de `baja` y `servido` debe usar estado y prioridad visibles, incluso en Todos los registros.
- La etiqueta del detalle necesita una regla propia y única en el motor. «Revisión humana» puede coexistir con prioridad alta, y «Solicitud sin confirmar» puede ser alta o media; se explica con evidencia y precedencia, no solo con el color.
- En escritorio, reservar ancho para la acción no basta cuando el texto se corta por `white-space: nowrap`; envolver las celdas mantiene legible el siguiente paso.
- La posición física de una fila es evidencia, no parte de la identidad ni del contenido de la línea: dos copias idénticas en filas distintas deben seguir consolidadas. Al recuperar la procedencia de un correo ya persistido, se contrasta su huella y se conserva la primera fila coincidente.
