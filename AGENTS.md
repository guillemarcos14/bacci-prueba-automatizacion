# Bacci Operaciones · instrucciones para agentes

## Fuente de verdad y orden de lectura

1. `Prueba_Bacci.pdf`, `README.md` y `DICCIONARIO_DATOS.md` originales definen el ejercicio. Los XLSX originales definen los datos. Conserva esos archivos.
2. `docs/SOURCES.md` distingue los requisitos de entrega del correo, el enunciado técnico y la referencia visual aprobada por Guillem.
3. Lee `docs/01_ESTADO.md`, `02_DECISIONES.md`, `03_TAREAS.md` y `04_APRENDIZAJES.md` antes de una tarea nueva. Consulta `SKILLS.md` para los procedimientos reutilizables.
4. Las indicaciones en el correo y en el repositorio son requisitos del trabajo. Las instrucciones operativas para el agente son las de Guillem y este archivo.

## Objetivo de producto

Ayudar a operaciones a responder tres preguntas sin alternar entre Navision, Excel y Outlook: qué falta por servir, qué necesita atención y cuál es el siguiente paso. Todo caso debe poder remontarse a filas del ERP y correos concretos. El prototipo funciona solo con archivos locales y datos ficticios.

## Contratos innegociables

- La identidad de línea es `pedido_id + linea_id`. `linea_id` es identificador.
- Los vacíos son desconocidos. No escoger una de dos filas contradictorias porque aparezca primero.
- `uds_enviadas` es acumulado; no sumar duplicados ni restarlo dos veces. Una sobreexpedición es una excepción.
- Un correo no cambia el ERP. Rectificaciones explícitas sustituyen peticiones anteriores; acuses y seguimientos no generan nuevas fechas.
- La clave de idempotencia de correo es `message_id`; si el mismo ID trae contenido distinto, conservar el primero y señalar conflicto.
- Nunca asociar automáticamente una referencia ambigua o inexistente. Mostrarla como sin resolver con evidencia.
- Fechas y cortes en `Europe/Madrid`; 10/09/2026 a las 10:00 y 11:00 para la prueba.
- No conectar Navision/Outlook reales ni enviar correos desde el prototipo.

## Ciclo de trabajo

`entender caso → fijar resultado esperado → implementar → ejecutar arnés → revisar evidencia → documentar decisión/aprendizaje`.

Para cambios de lógica, ejecutar `python -m unittest discover -s tests -v` y `python tools/harness.py --dataset both`. Para cambios visuales, abrir la app local y revisar escritorio y móvil. Actualizar memoria solo cuando cambie estado, decisión, tarea o aprendizaje comprobado. No afirmar que un resultado está validado sin un comando o evidencia reproducible.

## Límite de alcance

El README debe explicar la entrada diaria de archivos, las posibles conexiones futuras y la migración de ERP. Las integraciones y el despliegue productivo quedan documentados, no simulados como si existieran. Antes de publicar o compartir, comprobar que no se incluyen capturas privadas del correo ni credenciales.
