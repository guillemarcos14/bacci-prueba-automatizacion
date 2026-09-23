# Arnés de validación

## Comandos

```powershell
python -m unittest discover -s tests -v
python tools/harness.py --dataset both --output reports/validation.json
```

El arnés crea bases temporales limpias para cada tamaño de datos; ejecuta el corte inicial, incorpora el lote y repite el lote. El JSON guarda cada esperado y obtenido, hashes, conteos y milisegundos. El comando devuelve error si un oráculo falla.

## Oráculos

- Cálculo: P-26004 tiene 250 pendientes; P-26003 tiene 300 tras consolidar duplicado idéntico; P-26009 conserva pendiente desconocido por contradicción; P-26008 no muestra backlog negativo por sobreexpedición.
- Correo: P-26002 muestra 12/09 inicialmente, 13/09 tras la actualización, cuatro correos vinculados y el ERP intacto; P-99999 queda sin resolver; la cancelación de P-26001/20000 aparece aun con 0 pendientes.
- Procedencia: cada fila de pedidos conserva archivo, hoja y número de fila; los correos repetidos mantienen la ubicación de la primera entrega; el detalle conserva pedidas, enviadas acumuladas y pendientes.
- Idempotencia: muestra 24 correos iniciales únicos, completo 3.800, lote +3, segunda pasada +0, digest idéntico entre las dos últimas pasadas.
- Impacto por carga: actualización con dos casos modificados y repetición con cero; fecha solicitada 12/09 → 13/09 en P-26002; filtro de revisión humana con 7 casos en muestra y 767 en completo.
- Ambigüedad: P-30168 conserva las solicitudes activas de 21/09 y 24/09, sin elegir la última; 43 casos del conjunto completo presentan fechas incompatibles y requieren aclaración.
- Invariantes globales: todas las líneas sin duplicados tienen el pendiente correcto; cada evidencia conserva archivo/hoja/fila y mensaje existente; todas las etiquetas almacenadas concuerdan con el estado del caso.
- Rendimiento: tres duraciones por conjunto, medidas en esta máquina y guardadas en el informe; son una observación, no un SLA de producción.

## Límites del arnés

No comprueba capacidad logística, stock, validez de un contacto, acceso al vídeo ni disponibilidad de Navision/Outlook. Tampoco demuestra que reglas lingüísticas cubran todos los futuros correos de producción. Esas situaciones necesitan revisión humana o integración futura.
