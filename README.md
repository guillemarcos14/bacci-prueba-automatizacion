# Prueba de automatización

Del control de pedidos a la operación diaria

## El objetivo

Queremos conocer **cómo piensas, qué metodología sigues, cómo planteas un sistema y cómo presentas tus decisiones**.

Bacci suministra textil al *mass market*. Trabaja con un Navision antiguo, Excel y Outlook, y quiere modernizar su ERP en los próximos seis meses sin interrumpir la actividad.

Construye una **automatización y una aplicación sencilla** para que operaciones sepa **qué queda por servir, qué necesita atención y qué acción tomar**, cruzando pedidos y correos. Justifica tu priorización.

## Los archivos

| Archivo | Contenido |
| --- | --- |
| [Pedidos_full.xlsx](Pedidos_full.xlsx) | 20.000 filas de pedidos y un maestro de 250 clientes. |
| [Correos_full.xlsx](Correos_full.xlsx) | 4.000 filas de correos relacionados con la operativa. |
| [Pedidos_muestra.xlsx](Pedidos_muestra.xlsx) | 100 filas de pedidos y un maestro de 12 clientes. |
| [Correos_muestra.xlsx](Correos_muestra.xlsx) | 25 filas de correos. |
| [Correos_actualizacion.xlsx](Correos_actualizacion.xlsx) | 5 filas para probar la llegada de nuevos correos y la repetición de mensajes. |

Puedes empezar con los archivos `_muestra`, una selección de los `_full` con la misma estructura. Demuestra también el resultado completo. Consulta el [diccionario de datos](DICCIONARIO_DATOS.md).

Datos ficticios. Corte inicial: **10/09/2026 a las 10:00, hora de Madrid**. Trabaja con los archivos, sin conectar sistemas reales ni enviar correos.

## Qué construir

1. **Automatización.** Un proceso repetible que lea los archivos, cruce la información e incorpore nuevos correos sin editar filas manualmente.
2. **Aplicación mínima.** Una lista priorizada con pedido y línea, cliente, unidades pendientes, motivo y acción propuesta; filtros por cliente y prioridad; y un detalle con los datos y correos que justifican cada caso. Incluye los casos sin resolver. Basta una pantalla con su detalle, ejecutable localmente.
3. **Validación.** Justifica y ejecuta tus comprobaciones sobre cálculos, cruces y casos dudosos, mostrando resultados esperados frente a obtenidos. Demuestra la repetición del proceso y mide su tiempo con los archivos completos.

Los datos contienen anomalías. Explica tus supuestos, las limitaciones y qué decisiones dejarías a una persona.

## Prueba de actualización

1. Ejecuta el proceso con pedidos y correos iniciales.
2. Incorpora `Correos_actualizacion.xlsx` conservando los correos anteriores y los mismos pedidos. Nuevo corte: **10/09/2026 a las 11:00**.
3. Repite el paso 2. Demuestra los cambios de la primera incorporación y que repetirla no duplica mensajes ni altera los resultados.

Sirve con la muestra y el conjunto completo. Puedes recalcular todo o procesar las novedades. Esta prueba complementa tus propias validaciones.

## Qué valoraremos y qué entregar

**Priorizaremos la validación de los resultados y la utilidad para operaciones**, seguidas de la claridad de las decisiones y la facilidad de ejecución y mantenimiento.

Haz un **fork**. Conserva el enunciado y añade al README instrucciones, resultados, validaciones y una explicación breve de las entradas diarias, la conexión con Navision y Outlook y la migración del ERP.

Incluye un **vídeo dirigido al equipo de Bacci** con este orden: **problema** y cómo lo has entendido; **proceso** seguido y decisiones para llegar a la solución; **demostración** de la solución y sus validaciones. Comparte las URL del fork y del vídeo con Bacci y comprueba el acceso.

El alcance es un **prototipo local**. Herramientas libres. Puedes usar IA explicando cómo verificaste su trabajo. Prioriza y documenta lo pendiente; las conexiones reales y la puesta en producción solo deben explicarse.

---

# Solución · Bacci Operaciones

![Vista de la cola operativa](docs/screenshots/desktop.png)

El [vídeo de presentación para Bacci](https://github.com/guillemarcos14/bacci-prueba-automatizacion/releases/download/demo-v5/Demo_Bacci.mp4) dura 10 min 36 s. Empiezo por el problema, explico el método desde el minuto 2:17 y enseño la aplicación desde el 4:46; la actualización y sus comprobaciones aparecen a partir del 8:28. La [captura móvil](docs/screenshots/mobile.png) muestra cómo se adapta la cola y [Control de cargas](docs/screenshots/control-cargas.png) muestra el efecto del lote de las 11:00.

## Ejecutar en local

Requiere Python 3.10 o posterior. Desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m bacci serve
```

Abre `http://127.0.0.1:8765`. La aplicación usa **siempre el conjunto completo**. La primera ejecución crea `data/operations.sqlite`, incorpora el lote de actualización y deja la vista en el corte de las 11:00; en esta máquina las dos cargas tardaron alrededor de 30 segundos. Esta base de la aplicación está separada de las bases usadas por los comandos de prueba. El servidor solo escucha en `127.0.0.1`. En Linux/macOS sustituye `\.venv\Scripts\python.exe` por `.venv/bin/python`.

La cola muestra los casos activos, con los más urgentes primero. **Prioridad → Alta** deja solo los casos prioritarios. **Tipo → Revisión humana** muestra los que tienen datos dudosos o requieren verificar una identidad; se puede combinar con cliente, prioridad y búsqueda.

La búsqueda encuentra valores de pedidos, líneas, clientes y correos vinculados: referencias, SKU, color, talla, cantidades, fechas, direcciones, asunto y cuerpo. Ignora mayúsculas y tildes, admite fechas `dd/mm/aaaa` e ISO y exige que coincidan todas las palabras escritas. `alta`, `media` y `baja` buscan la prioridad de casos activos; `servido` busca líneas ya servidas. Al escribir se abre **Todos los registros**, para que también puedan aparecer esas líneas. Los filtros seleccionados siguen activos.

«Sin resolver» reúne los correos que no se pueden vincular con seguridad. «Control de cargas» guarda el historial de cada procesamiento y permite repetir el lote. Muestra mensajes nuevos, repetidos y en conflicto, el tiempo y la huella del resultado. En la columna **Cambios** se puede ver qué casos variaron, comparar el antes y el después y abrir la ficha actual. Las cargas guardadas antes de añadir esta comparación no tienen ese detalle retrospectivo.

## Reproducir la prueba paso a paso

En una copia limpia o después de apartar `data/sample.sqlite`:

```powershell
python -m bacci init --dataset sample
python -m bacci update --dataset sample
python -m bacci update --dataset sample
python -m bacci summary --dataset sample
python -m unittest discover -s tests -v
python tools/harness.py --dataset both --output reports/validation.json
```

Repite con `--dataset full` para el proceso manual completo. El arnés siempre crea bases temporales nuevas y deja `reports/validation.json` con resultados esperados frente a obtenidos, hashes y tiempos de ambos tamaños. También puedes ejecutar `python -m bacci demo --dataset sample` en una base que aún no exista. La muestra queda reservada a CLI, pruebas y validación; nunca se ofrece en la interfaz.

## Resultados y decisiones

| Comprobación | Muestra | Completo |
| --- | ---: | ---: |
| Filas de pedidos | 100 | 20.000 |
| Líneas únicas | 98 | 19.400 |
| Correos iniciales únicos | 24 | 3.800 |
| Duplicados iniciales ignorados | 1 | 200 |
| Mensajes nuevos del lote | 3 | 3 |
| Mensajes nuevos al repetir | 0 | 0 |
| Casos operativos tras el lote | 90 | 17.423 |
| Casos sin resolver | 2 | 569 |
| Registros consultables, incluidas líneas servidas | 100 | 19.969 |
| Casos que cambian a las 11:00 | 2 | 2 |
| Casos que cambian al repetir | 0 | 0 |
| Revisión humana | 7 | 767 |
| Validaciones del arnés | 38/38 | 38/38 |

Los tiempos medidos están en [`reports/validation.json`](reports/validation.json) y resumidos en [`reports/VALIDATION.md`](reports/VALIDATION.md); pueden variar en otra máquina. En la actualización, la fecha solicitada para P-26002 pasa del 12/09 al 13/09. Un acuse posterior no vuelve a cambiarla. Al repetir el lote se conservan los correos y el mismo `output_sha256`. La fecha del ERP tampoco cambia. La prioridad y sus motivos se explican en [`docs/PRIORITY.md`](docs/PRIORITY.md).

Los **cortes de las 10:00 y las 11:00** son dos fotografías del mismo ejercicio, ambas del **10/09/2026, hora de Madrid**. A las 10:00 se cargan los pedidos y los correos iniciales disponibles hasta entonces. A las 11:00 se mantienen esos pedidos y correos y se incorpora `Correos_actualizacion.xlsx`: tres mensajes nuevos y dos reentregas. Cambian dos casos: P-26002 recibe una rectificación de fecha solicitada y P-26004 un seguimiento; el ERP no se modifica. Reprocesar el lote de las 11:00 añade cero mensajes y cambia cero casos. Estas horas son límites temporales de la prueba, no plazos de entrega de los pedidos.

### Qué cuenta cada vista

Las 20.000 filas de pedidos del XLSX representan 19.400 líneas únicas identificadas por `pedido_id + linea_id`. **Cola de trabajo** reúne 16.854 líneas con algo que atender y 569 correos sin correspondencia, en total **17.423 casos**. **Todos los registros** añade las 2.546 líneas ya servidas: **19.969 registros**. **Sin resolver** muestra únicamente los 569 correos sin correspondencia fiable; ya están incluidos en las otras dos cifras y no se suman otra vez. Una línea servida es un estado, no una prioridad; al filtrar `Alta`, `Media` o `Baja` solo aparecen casos activos.

### Qué controla cada carga

Cada ejecución registra el corte, número de casos, tiempo y huella del resultado. **Nuevos** cuenta ID de mensaje válidos no vistos antes. **Repetidos** cuenta ID ya vistos cuyo contenido es idéntico; no vuelven a entrar. **Conflictos** cuenta ID existentes con contenido diferente y registros con ID o fecha de recepción inválidos; requieren revisión. Las cifras pertenecen al lote de esa fila, no son acumulados. En el lote entregado hay 3 nuevos y 2 repetidos; al repetirlo hay 0 nuevos y 5 repetidos. En un uso real, el responsable de operaciones podría detectar cortes incompletos o retrasados, mientras soporte investigaría conflictos y cambios inesperados de la huella. Este prototipo solo procesa los XLSX locales.

Las filas idénticas se consolidan. Si dos filas de la misma línea discrepan, no se elige una arbitrariamente; las cantidades contradictorias o sobreexpedidas dejan el pendiente como desconocido y abren revisión. Las fechas vacías son desconocidas. Si dos peticiones activas indican fechas distintas sin rectificación explícita, se muestran ambas y se pide aclaración: el correo más reciente no prevalece automáticamente. Un correo sin referencia fiable genera un caso sin resolver. Las sugerencias por SKU nunca se vinculan automáticamente. Un contacto nuevo o remitente no coincidente requiere verificar identidad. Ninguna solicitud modifica el ERP por sí sola. La regla exacta y la precedencia de las seis etiquetas del detalle constan en [`docs/PRIORITY.md`](docs/PRIORITY.md).

## Procedencia de lo mostrado

Los pedidos, clientes y mensajes se leen de los XLSX entregados en el enunciado; la aplicación no inventa filas ni correos. Por ejemplo, `msg-13756` está en `Correos_full.xlsx`, hoja `Correos`, fila 2622, a las 23:36 del 09/09/2026. Menciona `P-X003756 / 10000`, referencia ausente de `Pedidos_full.xlsx`; por eso aparece en «Sin resolver». Los dominios `.example` pertenecen a los datos ficticios de la prueba, no a sistemas de producción.

La aplicación calcula unidades pendientes, prioridad, motivo y siguiente paso; también registra los tiempos, conteos y huellas de cada carga. Los textos de interfaz y el símbolo de «Bacci Operaciones» son diseño propio. En cada ficha se ven las unidades pedidas, enviadas acumuladas y pendientes, junto a las filas originales del ERP. Cada correo conserva remitente, destinatario, texto, `message_id`, archivo, hoja y fila. Así es posible comprobar de dónde sale cada conclusión.

## Validación y mantenimiento

[`docs/HARNESS_ENGINEERING.md`](docs/HARNESS_ENGINEERING.md) explica qué se comprueba y cómo repetirlo. Las pruebas cubren cálculos, duplicados, sobreexpedición, negaciones, rectificaciones, correos con varias líneas, referencias inválidas, origen de los datos y repetición sin duplicados. Una de ellas evita que la fecha `12/09/2026` se confunda con `linea_id=2026`.

Dejé las decisiones y los resultados de la revisión en [`docs/`](docs/), especialmente en [`docs/AUDIT.md`](docs/AUDIT.md). Usé IA como apoyo para programar y revisar; contrasté los cruces y los cálculos con casos conocidos y con el conjunto completo. Las decisiones sobre stock, logística y autorización de contactos siguen correspondiendo a personas de Bacci.

## Entrada diaria e integración futura

En el trabajo diario, Navision exportaría pedidos y clientes con las mismas columnas. Outlook aportaría los mensajes nuevos, cada uno con su `message_id`. El proceso guardaría los ID recibidos, actualizaría la cola y registraría el corte, los conteos, el tiempo y los errores. Aquí solo se usan los XLSX de la prueba y su lote de actualización; no hay conexión a sistemas reales ni envío de respuestas.

Para la migración del ERP durante seis meses, mantendría este modelo de casos separado del origen mediante adaptadores de entrada. Ejecutaría Navision y el nuevo ERP en paralelo, comparando identificadores, cantidades y fechas por corte antes de cambiar la fuente. Los correos seguirían siendo eventos externos, no escrituras directas en el ERP. La operación continuaría con una única cola y trazabilidad de la procedencia. Este plan se documenta; no se despliega en la prueba.

## Pendiente fuera del prototipo

Verificar permisos y contactos reales, consultar stock/capacidad, enviar respuestas, registrar decisiones y escribir cambios aprobados en el ERP; añadir monitorización, control de acceso y reconciliación de versiones de exportaciones. Estos pasos requieren los sistemas y responsables de Bacci.
