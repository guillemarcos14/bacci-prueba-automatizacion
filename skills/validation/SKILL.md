# Validación de negocio y técnica

1. Ejecuta `python -m unittest discover -s tests -v`.
2. Ejecuta `python tools/harness.py --dataset both --output reports/validation.json`.
3. Comprueba el resumen `76/76`, los tiempos inicial/actualización/repetición, los dos casos afectados, las fechas incompatibles y los detalles esperado/obtenido de `reports/validation.json`.
4. Revisa manualmente P-26002 (rectificaciones 12→13), P-26004 (250 pendientes y vencido), P-26009 (duplicado contradictorio), P-26001/20000 (cancelación pese a 0 pendientes), P-99999 (sin vínculo).
5. Para cambios de UI, arranca `python -m bacci serve --dataset sample`, prueba filtros, búsqueda, navegación y actualización. Comprueba también `/api/health`.

Un arnés verde no acredita stock, capacidad logística, identidad del nuevo contacto ni aprobación de cambios del ERP. Esas decisiones permanecen humanas.
