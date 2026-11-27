# Revisión del repositorio — 27 de noviembre de 2026

[Documentación](../README.md) · [English](../en/project-review.md)

## Resultado y alcance

El proyecto tiene un montaje instalado que funciona y un paquete de firmware
permanente independiente. La confusión venía principalmente de la voz utilizada,
varios puntos de entrada y revisiones antiguas que parecían instrucciones actuales.
La revisión corrigió esos problemas de presentación sin cambiar el controlador.

Se revisaron el árbol actual, las responsabilidades del firmware, configuración,
documentación bilingüe, pruebas, empaquetado y el problema ya identificado en el
historial Git. Es una revisión del repositorio, no una nueva prueba en vehículo,
certificación eléctrica ni auditoría exhaustiva de seguridad.

Los resultados del montaje instalado que aparecen en la introducción son mi
experiencia con mi F-150 FX4 2007 5.4 L 3V. Las comprobaciones locales descritas
abajo son evidencia de software separada.

## Hallazgos y cambios

| Hallazgo | Motivo de confusión | Resolución |
| --- | --- | --- |
| Narrador externo | «El propietario informó» hacía que mi proyecto pareciera contado por otra persona | Primera persona en ambos README principales, README del firmware, guías de hardware y changelog |
| Instrucciones mezcladas con notas de limpieza | Detalles de conexión a GitHub distraían de la instalación | Guía de publicación con un procedimiento repetible; resultados fechados en este informe |
| Varios archivos parecían finales | `ESQUEMA_FINAL` y distintos `main.py` parecían alternativas actuales | Índice con un único paquete permanente y guías actuales; catálogos de los archivos antiguos |
| Paquetes duplicados sin explicación | Cinco módulos de `legacy/pico_prueba_camioneta/` coinciden con `legacy/`, pero el lanzador cambia | Se documentó el paquete histórico de copia al dispositivo; no representa otra rama final mantenida |
| Documentación incompleta parecía instalación pendiente | Frases antiguas de validación pendiente contradecían semanas de uso | Las guías separan detalles faltantes para reproducir el montaje de su uso ya realizado |
| Número de pruebas ambiguo | «51 pruebas» podía entenderse como 51 del firmware final | Se distinguen 18 del controlador permanente y 33 regresiones históricas |
| Política de finales de línea inconsistente | El editor pedía LF, pero Git dejaba algunos archivos al ajuste de plataforma | LF predeterminado para texto, conservando excepciones binarias; sin reescribir el firmware |
| Cachés borradas seguían en el historial | Un árbol limpio podía confundirse con un historial publicable limpio | Se conserva la exportación de fuentes sin historial y se explica la decisión por separado |

La convención queda definida: primera persona para historia y resultados propios,
instrucciones directas para instalar, lenguaje técnico neutral para el
funcionamiento e informes fechados para hallazgos. Ambos idiomas siguen la misma
organización.

## Estructura actual

| Ubicación | Estado | Destinatario |
| --- | --- | --- |
| [Introducción](../../README.es.md) | Historia y punto de entrada actual | Todos |
| [Índice](../README.md) | Orden de lectura | Quien construye o contribuye |
| [pico_final](../../pico_final/README.md) | Única fuente de firmware permanente | Instalación y mantenimiento |
| [Hardware](hardware.md), [configuración](configuration.md), [instalación](installation.md) | Guías actuales | Reproducción del montaje |
| [tests](../../tests/) | Simulaciones del controlador permanente | Desarrollo de firmware |
| [examples](../../examples/README.md) | Prueba aislada opcional del Monitor | Diagnóstico de banco |
| [legacy](../../legacy/README.md) | Experimentos y registrador conservados | Diagnóstico histórico |
| [archive](../archive/README.md) | Planos y notas anteriores | Referencia de desarrollo |
| [tools](../../tools/) | Comprobaciones y empaquetado en PC | Publicación |

No hizo falta otra reorganización masiva. Conservar los paquetes históricos
permite entender ensayos anteriores; los puntos de entrada claros evitan que
compitan con el programa instalado. Los archivos antiguos no son destinos de
instalación actual.

## Revisión del firmware

El lanzador apaga GP5, GP18 y el LED integrado antes de importar
`pico_final.runtime`. Las responsabilidades están separadas:

- `config.py`: calibración efectiva, pines, tiempos y funciones habilitadas.
- `controller.py`: estabilidad del comando, clasificación Hall, destino,
  asentamiento y presupuesto acumulado de marcha.
- `runtime.py`: estado aplicado de motor/freno, Monitor, recuperación, watchdog,
  extensión del reloj y eventos de consola acotados.
- `hardware.py`: GPIO, PWM, lecturas ADC, freno y apagado.

La configuración importante se conserva:

| Comportamiento | Valor efectivo |
| --- | --- |
| Comando | GP15=0 cierra; GP15=1 abre |
| Extremos | A Hall alto/cerrado; B Hall bajo/abierto; `A_DIRECTION=1` |
| PWM | Inicial 40%, marcha 70%, rampa 20 ms, frecuencia 20 kHz |
| Presupuesto | 3000 ms de marcha por destino confirmado |
| Pausa y freno | Pausa de 300 ms al arrancar/invertir/reanudar; freno de 50 ms |
| Hall A | Entrada ≥40000; retención por encima de 35000 |
| Hall B | Entrada ≤26000; retención por debajo de 31300 |
| Hall válido | Cada lectura cruda estrictamente entre 2000 y 63500 |
| Filtros | Comando 50 ms; clasificación Hall 30 ms; asentamiento 150 ms |
| Arranque | Validación de 500 ms; sin espera adicional de cinco segundos |
| Recuperación | Espera 30 s y luego un segundo de Hall válido y comando sin cambios |
| Monitor | Apertura confirmada y asentada, sin marcha ni freno |
| Indicadores | LED integrado apagado; LED externos de orden/fallo |
| Registro | Sin archivos; cola de consola acotada en RAM |

Un nuevo destino confirmado renueva el timeout; ruido y pausas no. El freno no
consume presupuesto de marcha. A/B identifican rangos Hall, mientras el signo de
dirección identifica el cableado: cambiar `OPEN_END` no obliga a invertir
`A_DIRECTION`.

Las muestras crudas fuera de rango detienen el control aunque la media parezca
válida. Los fallos del bucle permiten recuperación; una configuración inválida
queda bloqueada. Hay reintentos ilimitados, sin medición de corriente ni diagnóstico
de atasco. Monitor liberado/alto durante movimiento o fallo no prueba cierre físico.

La recuperación descrita corresponde al bucle de control y a la ruta explícita
tras watchdog. Las importaciones y construcción inicial del hardware ocurren antes
del bucle protegido; no debe suponerse que archivos faltantes o fallos de arranque
siguen la misma recuperación. Esta revisión no modificó esas rutas.

## Hardware y datos pendientes para reproducirlo

La guía reúne conector, tierra común, positivos de 5 V/12 V separados, conexiones
sincronizadas del driver, filtro Hall y Monitor de colector abierto. Incluye las
mediciones aproximadas de 12 V alto y 0 V bajo con la PCM conectada. El nivel alto
lo suministra la PCM.

Para reproducir exactamente el montaje físico aún faltan datos de la instalación:

| Detalle faltante | Qué resuelve |
| --- | --- |
| Circuito exacto de protección de entrada y fusible | El bloque de protección actual no equivale a un esquema completo de componentes |
| Variantes concretas de módulos, sensor y transistor | Marcas y módulos parecidos pueden tener otra disposición de pines |
| Fotos, vistas de conectores, fijación y distancia sensor/imanes | La calibración depende del mecanismo físico |
| Esquema completo del montaje real | El archivo contiene revisiones e ilustración, no un único plano definitivo |
| Versión MicroPython probada | La placa está documentada; la compilación exacta instalada no está fijada |

Son pendientes de documentación. El montaje actual ya está en uso. No se agregaron
afirmaciones de compatibilidad general, calificación de transitorios ni margen de
corriente del driver. Tampoco se eligieron componentes nuevos.

## Validación y límites

- **18 pruebas del controlador permanente:** tiempos, comandos estables,
  presupuesto de marcha, freno/Monitor, Hall, pérdida de posición, recuperación,
  configuración, consola, desbordamiento del reloj, adaptador y cancelación.
- **33 pruebas históricas:** controlador anterior, registrador y menú de pruebas.
- **Repositorio:** sintaxis sin importar hardware, enlaces locales Markdown,
  licencia y búsqueda dirigida de patrones de rutas privadas/tokens.
- **Conservación:** los seis archivos `pico_final/*.py` coinciden byte por byte
  con el respaldo previo a la organización; Git no muestra cambios de firmware.
- **Paquetes:** lectura y verificación de ambos ZIP; extracción independiente de
  las fuentes y ejecución de comprobaciones/pruebas. Manifiestos con hashes reales.

La simulación no demuestra corriente, inmunidad al ruido, aceptación de la PCM ni
comportamiento con otra carga. La búsqueda de texto no es una auditoría completa
de credenciales ni metadatos binarios. Los enlaces externos no se verifican todos.
GitHub Actions está configurado, pero no se observó ejecución remota durante esta
revisión. No se conectó ni se programó ninguna placa.

## Estado de publicación

GPL-3.0-only está elegida e incluida. Ambos paquetes conservan la licencia y sus
manifiestos SHA-256. ZIP generados, registros, entornos y respaldos privados del
Pico quedan fuera de Git.

La primera limpieza identificó rutas locales en ocho cachés Python de los cinco
commits originales. Borrarlas en otro commit no elimina sus copias históricas.
Un repositorio nuevo desde el ZIP limpio evita arrastrarlas; publicar el historial
original requiere limpiarlo por separado. Esta revisión no reescribió historial,
no hizo force push ni cambió visibilidad.

Los nombres de ZIP usan la versión del firmware. Un cambio documental requiere
regenerar hashes y elegir otra etiqueta de publicación cuando se publique. La
[guía](../RELEASING.md) lo explica ahora explícitamente.

## Próximos pasos

Las correcciones de voz y organización están implementadas. Para publicar queda
elegir la ruta de historial, ejecutar comprobaciones en ese repositorio y publicar
fuentes y firmware bajo una etiqueta. Los detalles físicos se pueden completar
desde el montaje instalado sin modificar el firmware que funciona. Organizar la
documentación no requiere volver a ajustar el motor.
