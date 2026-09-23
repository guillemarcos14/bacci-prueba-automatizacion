# Procedimientos reutilizables

Estos documentos son habilidades locales del proyecto y explican cómo repetir trabajos sin perder criterios:

| Procedimiento | Uso |
| --- | --- |
| [`skills/ingestion/SKILL.md`](skills/ingestion/SKILL.md) | Incorporar un lote nuevo de correos y verificar la conservación de los anteriores. |
| [`skills/validation/SKILL.md`](skills/validation/SKILL.md) | Ejecutar oráculos de negocio, idempotencia, conjunto completo y medición. |
| [`skills/visual-review/SKILL.md`](skills/visual-review/SKILL.md) | Comprobar fidelidad a la imagen aprobada y utilidad real para operaciones. |

Cada procedimiento remite a los contratos de `docs/LOOP_ENGINEERING.md` y `docs/HARNESS_ENGINEERING.md`. Si cambia una regla de negocio, actualizar antes el resultado esperado y después el código y la memoria de decisiones.
