# Ingesta repetible

1. Verifica que el XLSX conserva la hoja y columnas descritas en `DICCIONARIO_DATOS.md`.
2. Para un conjunto nuevo, ejecuta `python -m bacci init --dataset sample` o `--dataset full`.
3. Incorpora `Correos_actualizacion.xlsx` con `python -m bacci update --dataset ...`; el proceso guarda correos anteriores por `message_id` y reconstruye los casos.
4. Repite el mismo comando. Debe informar `added_messages=0` y conservar `output_sha256`.
5. Si llega un mismo `message_id` con otro contenido, no sobrescribir silenciosamente; el contador `conflicting_messages` obliga a investigación.

No editar filas de origen. Para una demostración limpia usa una base nueva o el arnés en directorio temporal. El UI local ofrece la misma actualización desde «Ejecuciones».
