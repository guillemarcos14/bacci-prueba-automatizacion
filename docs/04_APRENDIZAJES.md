# Aprendizajes verificados

- La muestra tiene 100 filas de pedidos, 98 líneas únicas, una duplicación idéntica y otra contradictoria. El conjunto completo tiene 20.000 filas y 19.400 líneas únicas.
- La muestra inicial trae 25 filas de correo y 24 `message_id` únicos. El conjunto completo trae 4.000 filas y 3.800 ID únicos. El lote de actualización añade tres mensajes y contiene dos reentregas; su segunda ejecución añade cero.
- P-26002 demuestra que una rectificación posterior cambia la **petición vigente** de 12/09 a 13/09; el acuse posterior no crea otra fecha ni cambia el ERP.
- Una fecha `dd/mm/aaaa` contiene barras; el analizador no puede tratar `/2026` como si fuera `linea_id`. Una prueba cubre este fallo y la línea de P-33853.
- Los casos sin referencia fiable tienen valor operativo si permanecen en una cola visible con el correo original y una acción de investigación.
