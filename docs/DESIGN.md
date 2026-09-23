# Identidad visual aprobada

La imagen ERP/POS aportada por Guillem es la autoridad estética, no funcional. La aplicación usa un fondo gris suave a pantalla completa con degradado lila, azul y verde en la zona inferior; superficies blancas cálidas; texto grafito; navegación y pestañas en píldoras; lima pálido para sección y caso seleccionados. El ancho se adapta a la ventana para dar más espacio a la tabla y el detalle.

La marca lateral presenta «Bacci» y «Operations» en dos líneas con el mismo tamaño y peso. La barra gris de vistas deja una separación de 8 px respecto a la tarjeta de trabajo.

La píldora blanca de la vista activa («Cola de trabajo» o «Todos los registros») ocupa los 41 px de altura de la barra gris, con los extremos redondeados. La primera pestaña llega hasta el borde izquierdo de la barra, sin franja gris entre ambas curvas, y centra el texto con 17,5 px a cada lado. En la tarjeta de caso, «Fecha solicitada» distingue una petición por correo de la fecha del ERP; «Qué sabemos» muestra primero el motivo concreto y la nota de verificación se mantiene bajo el siguiente paso.

## Acabado de escritorio

La interfaz usa Inter Variable servida desde el propio proyecto (`bacci/web/InterVariable.woff2`, licencia OFL adjunta). La jerarquía tipográfica evita texto auxiliar diminuto: títulos de 16–20 px y cuerpo, tablas y etiquetas de 12–13 px. Los tres iconos de navegación comparten tamaño, trazo y remates. Se eliminó el avatar «BO» porque no representaba a un usuario ni ofrecía una acción.

Tarjetas y controles comparten bordes finos, radios de 16 y 8 px y tonos neutros de mayor contraste. Las etiquetas permanecen alineadas con sus filtros en escritorio; cada control mide 34 px de alto. En «Control de cargas», las fechas se muestran abreviadas para caber en la tabla y conservan el valor completo como título. El acabado se comprobó a 1680 y 1280 px sin desbordamiento horizontal.

## Traslado funcional

La tabla principal concentra pedido/línea, cliente, unidades pendientes, motivo y acción. El detalle añade ERP frente a petición vigente, anomalías y correos concretos. «Sin resolver» y «Control de cargas» son vistas operativas, no elementos decorativos. La prioridad alta se obtiene con el filtro de la cola, sin una pestaña duplicada. No se reproducen POS, nóminas, ventas ni otros apartados de la referencia.

## Reglas de uso

- La prioridad se expresa en texto y un punto discreto; el color no es la única señal.
- Los filtros y la búsqueda se mantienen junto a la tabla. Las filas pueden seleccionarse con teclado.
- En móvil, cada fila pasa a una ficha legible con todas las acciones visibles.
- La vista de detalle nunca confunde solicitud por correo con dato ERP confirmado.
