# Estado actual

**23/09/2026.** Prototipo local completo en este repositorio. Motor de conciliación, base SQLite, CLI, API local e interfaz operativa implementados. El arnés ha pasado 20 comprobaciones en muestra y 20 en completo; la última evidencia reproducible está en `reports/validation.json`. La interfaz se ha revisado en escritorio y móvil, con capturas en `docs/screenshots/`. El diseño usa la dirección visual aprobada por Guillem. El README documenta ejecución, resultados y límites. El vídeo narrado actualizado se publica como recurso de la versión `demo-v2` del fork.

La aplicación no accede a Navision ni Outlook reales y no envía correos. Las decisiones que requieren stock, logística o verificación de identidad quedan para una persona.

**Revisión de Guillem, 23/09/2026.** Fondo extendido a toda la pantalla; búsqueda sobre los valores importados; selector de muestra/completo; vista de todos los registros, incluidas líneas servidas. Validación repetida con 20/20 oráculos por conjunto y pruebas de interfaz en escritorio y móvil. La cola mantiene 90 casos en muestra y 17.423 en completo; la vista de registros muestra 100 y 19.969, respectivamente.
