# Metodología de representación de indicadores EFQM 2028

**Revisión del 26/11/2026.** Documento de trabajo de la Biblioteca de la Universidad de Sevilla (BUS). Las decisiones consolidadas describen el prototipo vigente. La selección de indicadores, las metas oficiales y los requisitos de la evaluación de 2028 siguen sujetos a validación.

[Estándar gráfico](#9-estándar-de-representación-gráfica) · [Referencias](#12-referencias-bibliográficas-y-normativas) · [Registro de decisiones](#13-registro-de-decisiones) · [Evidencias predictivas](#anexo-técnico-y-resultados-reproducibles)

## 1. Propósito y alcance

El estándar organiza la representación individual de indicadores de resultados para facilitar su lectura en la evaluación, la planificación estratégica y las decisiones de gestión. La restricción de una imagen por indicador procede del encargo del proyecto y se adopta como condición de diseño. Cada lámina integra el título, las unidades, el periodo, las series pertinentes, la leyenda, la fuente y las advertencias necesarias para interpretarla fuera de la web.

La interfaz sirve para que el equipo y el asesor comparen configuraciones. La imagen de evaluación es la exportación de una configuración revisada, que puede leerse de forma autónoma. Los cuatro indicadores son casos de prueba del modelo gráfico. La selección definitiva y la versión del modelo aplicable en 2028 quedan pendientes de aprobación.

## 2. Fuentes de información

El grupo de Estadísticas de REBIUN mantiene el proceso de recogida y los anuarios. El prototipo accede a los datos a través de REBIUN Data Explorer, que publica un fichero longitudinal y un directorio de bibliotecas. La revisión de origen está fijada en [indicadores.json](indicadores.json). Para reproducir el prototipo se usan los CSV de esa revisión. La ficha de REBIUN de cada campaña sirve para contrastar definiciones cuando cambian rótulos o códigos. [REBIUN, Estadísticas](https://www.rebiun.org/grupos-trabajo/estadisticas) · [Revisión de los datos](https://github.com/mvarort/datos-rebiun/tree/25996fc11eb8212e11a114b58884b3741c6194bd/data)

El localizador de una observación es la combinación de `Anio`, `Codigo_Biblioteca_REBIUN` y `Codigo_Tecnico`. La BUS se identifica con el código `67` en `bibliotecas_rebiun.csv`. El campo `Modalidad` del directorio se aplica a todas las anualidades de esta revisión. La tabla reproduce el alcance operativo de los campos en la fuente longitudinal. [CSV de origen](https://github.com/mvarort/datos-rebiun/tree/25996fc11eb8212e11a114b58884b3741c6194bd/data) · [Tratamiento](datos.py)

| Código | Variable y unidad de origen | Uso |
|---|---|---|
| `NPRESTDOMIC` | Préstamos domiciliarios, recuento | Indicador directo. Cambia el rótulo desde 2022 y el código REBIUN pasa de 6.2 a 6.2.1 en 2023. Equivalencia de campaña pendiente de comprobar. |
| `NMONPAGOLIC` | Monografías electrónicas de pago, recuento | Indicador directo. |
| `NUSUARIOPROP` | Personas usuarias propias, personas | Filtro de elegibilidad y numerador de personas por puesto. |
| `NPUESTOSLECT` | Puestos de lectura, recuento | Denominador de personas por puesto. |
| `GASTOINFOELECT` | Gasto en información electrónica, euros | Numerador del porcentaje. |
| `GASTORECINFO` | Gasto en recursos de información, euros | Denominador del porcentaje. |

Se calculan las razones por biblioteca y año antes de agregar. Personas por puesto divide `NUSUARIOPROP` por `NPUESTOSLECT`. El porcentaje divide `GASTOINFOELECT` por `GASTORECINFO` y multiplica por 100. Un componente ausente, un denominador nulo o un resultado fuera del dominio natural deja el resultado derivado ausente. Los centros elegibles con resultado ausente se mantienen en el fichero de grupo y quedan fuera del agregado del año. Los ceros válidos se conservan. La generación predictiva exige una serie BUS completa en la ventana histórica cargada. [Reglas y controles](datos.py) · [Prueba de denominadores](test_indicadores.py)

| Naturaleza | Procedencia y localizador |
|---|---|
| Observado | Valor del CSV original o razón calculada sobre datos observados de la misma biblioteca y año. Campo `bus` de `serie.csv`. |
| Calculado | Razones, elegibilidad, mediana y extremo anual. `grupo.csv` y campos `benchmark`, `referencia`, `elegibles` y `con_dato` de `serie.csv`. |
| Previsto | Resultados futuros estimados por el modelo publicado. Campos `prevision`, `prediccion_inferior_95` y `prediccion_superior_95`. |
| Planificación ilustrativa | Metas y límites configurados para ensayar la representación. Campos `meta`, `limite` y `naturaleza_plan`. |

Los originales se conservan. Los CSV procesados son instantáneas. Ante una campaña nueva o una corrección, se registra la revisión, se contrastan las definiciones y se regeneran y revisan los resultados afectados. [Configuración](indicadores.json) · [Instantáneas procesadas](datos_procesados/)

## 3. Dimensión temporal

Los diez años visibles, **2016–2025**, permiten observar trayectoria, variabilidad y la ruptura alrededor de 2020. Los periodos de **2026–2028** y **2026–2030** sirven respectivamente para la lectura de corto plazo y para ensayar un horizonte estratégico más amplio. Tres años es la vista inicial. Ambas vistas se obtienen del mismo ajuste a cinco años, por lo que coinciden los pronósticos de 2026–2028.

El periodo de ajuste se declara por indicador y aparece en la nota de la imagen. Puede ser más corto que el histórico dibujado cuando los datos antiguos describen otro régimen. La revisión anual es una pauta de mantenimiento que debe aplicarse al disponer de una campaña validada. Incluye comprobar si cambiaron las definiciones, la selección del modelo y la cobertura retrospectiva. [Configuración](indicadores.json) · [Generación de horizontes](generar.py) · [Métodos vigentes](#metodología-predictiva-revisada--25112026)


**Ventana de visualización (MR-16, 26/11/2026).** «Año inicial» y «Año final»
seleccionan un intervalo inclusivo del histórico disponible. El valor inicial
es 2016–2025 y se admite un único año. Los menús deshabilitan las opciones
que invertirían los extremos. Las vistas se generan a partir de una misma
serie calculada por indicador. Recortar solo decide qué registros se dibujan,
incluidas las referencias y las filas numéricas. El periodo de ajuste,
el modelo, la previsión, los intervalos y los valores de planificación
siguen siendo los de la serie original. El subtítulo y la nota identifican
la ventana visible y el periodo de ajuste.

La prospectiva se muestra si el año final coincide con el último año
observado de la serie. Cuando el recorte termina antes, la gráfica omite las
barras, filas, leyenda y controles futuros. Así se evita dibujar años
futuros separados del último resultado mostrado por años históricos
ocultos. Al restaurar el último año se recuperan el horizonte y las
opciones de visibilidad anteriores. El espacio por año y la escala se
adaptan al contenido, con un margen horizontal mínimo para las ventanas
más estrechas. El PNG conserva el periodo y los elementos de la vista activa.
[Generación de vistas](generar.py) · [Controles y exportación](selector.js)

## 4. Comparaciones externas

Cada año, el grupo externo incluye bibliotecas REBIUN clasificadas como presenciales que declaran **más de 40.000 personas usuarias propias**. La BUS se excluye del filtro del grupo externo y entra expresamente en el extremo de referencia. La pertenencia se recalcula cada anualidad. Las estadísticas usan únicamente casos válidos para el indicador.

- **Benchmark.** Mediana sin ponderar de los comparadores externos. Cada biblioteca contribuye un valor. La mediana representa el centro del grupo y es menos sensible a valores extremos que la media. Excluir a la BUS hace que su propio dato no desplace el punto de comparación. [OpenStax, §2.5](https://openstax.org/books/introductory-statistics-2e/pages/2-5-measures-of-the-center-of-the-data) · [Cálculo](datos.py)
- **Referencia del grupo (*Best in Class* como concepto).** Extremo anual entre los comparadores válidos y la BUS. Es el máximo para polaridad creciente y el mínimo para decreciente. Incluir a la BUS permite representar el extremo realmente observado en el conjunto de evaluación. Si lo alcanza, incluidos los empates, el marcador es rojo. La interfaz mantiene la denominación «Referencia del grupo». [Cálculo y marca de liderazgo](datos.py) · [Trazado](grafico.py)
- **Polaridad pendiente.** En gasto electrónico se utiliza el máximo como referencia descriptiva que incluye a la BUS, sin distintivo de liderazgo. La proporción presupuestaria requiere una interpretación estratégica acordada para valorar su evolución. [Configuración del porcentaje](indicadores.json)

El umbral de tamaño mejora la pertinencia del contraste, pero deja diferencias de población, servicios, cartera documental y prácticas de registro. Los recuentos absolutos siguen siendo sensibles al tamaño. Un cambio en la mediana o en el extremo puede proceder de cambios de composición, de resultados o de ambas cosas. `grupo.csv` permite reconstruir quién contribuye cada año. La comparación cuantitativa identifica diferencias y requiere investigar las prácticas y el contexto para interpretar sus causas. [APQC, metodología y normalización](https://www.apqc.org/How-Can-KPI-Definitions-Support-Valid-Comparison) · [Instantáneas](datos_procesados/)

## 5. Banda comparativa

La banda ocupa el espacio entre la mediana externa y la referencia anual. Para polaridad creciente se extiende hacia el máximo y para decreciente hacia el mínimo. Permite situar la BUS respecto al centro externo y al extremo del conjunto, incluido el caso en que la BUS define el extremo. Para polaridad pendiente indica un tramo descriptivo.

«Banda comparativa» es una denominación descriptiva del proyecto. Sus extremos son dos estadísticos observados, sin nivel de confianza ni estimación de error muestral. El rango intercuartílico se define mediante Q1 y Q3, mientras que esta banda utiliza la mediana y el extremo. Alcanzarla tampoco acredita excelencia. Se descartaron las superficies independientes porque duplicaban el área de referencia y la zona desde cero podía leerse como un umbral de desempeño. Las dos líneas y una sola banda permiten reconocer los extremos conservando el foco en las barras. [OpenStax, §2.3](https://openstax.org/books/introductory-statistics-2e/pages/2-3-measures-of-the-location-of-the-data) · [Trazado de la banda](grafico.py)

## 6. Metas y límites de gestión

| Elemento | Interpretación |
|---|---|
| Resultado observado | Evidencia cuantitativa de un ejercicio cerrado, directa o derivada. |
| Resultado previsto | Estimación puntual de un ejercicio futuro bajo el método y el periodo publicados. |
| Meta | Resultado que se desea alcanzar tras acordar prioridades, actuaciones y recursos. |
| Límite de gestión | Umbral que orienta revisión o intervención cuando se cruza en sentido desfavorable. |
| Benchmark | Centro externo de comparación para ese ejercicio. |
| Referencia del grupo | Extremo anual del conjunto de comparación, incluida la BUS. |
| Intervalo de predicción | Rango para una nueva observación anual bajo los supuestos del modelo. |

En polaridad creciente, la meta se sitúa en el sentido de valores mayores y el límite en el de valores menores. En polaridad decreciente se invierte el orden. El prototipo comprueba que la meta de personas por puesto queda por debajo del límite en todos los años. Con polaridad pendiente, los dos valores de gasto representan únicamente una prueba gráfica. **Todas las metas y límites actuales son ilustrativos y carecen de aprobación oficial.** [Configuración y validación](indicadores.json) · [Generación](generar.py)

Las previsiones informan sobre la trayectoria esperable y sus intervalos ayudan a valorar la magnitud del riesgo. La fijación de compromisos corresponde a la gestión y requiere justificar capacidad de intervención, recursos, tolerancias y prioridades. Los extremos predictivos carecen de una función automática de meta o límite. [Metodología predictiva y cobertura](#metodología-predictiva-revisada--25112026)

## 7. Metodología predictiva

Se contrastan el último valor observado, la media móvil de tres años, la regresión lineal, el suavizado exponencial simple y Holt con tendencia amortiguada. Ante una ruptura plausible se exploran ventanas recientes y modelos de intervención. También se ensayan transformaciones log y logit cuando ayudan a representar el dominio natural.

La validación usa orígenes expansivos. Cada ajuste utiliza los datos disponibles hasta su origen. El **MAE** resume el error absoluto medio y la **RMSE** es la raíz del error cuadrático medio, más sensible a errores grandes. Ambos se calculan en las unidades originales. Se comparan candidatos sobre los mismos orígenes y plazos. Las ventanas con pocos casos se presentan como sensibilidad. La selección publicada combina error comparable, parsimonia, naturaleza del indicador y plausibilidad del periodo. [Hyndman y Athanasopoulos, cap. 5 y 7](https://otexts.com/fpp3/) · [Implementación](revision_predictiva.py)

| Indicador | Ajuste vigente | Razón principal |
|---|---|---|
| Préstamos | Media móvil, 2022–2025 | En los orígenes comunes 2022–2024, MAE medio 27.844 para la media móvil y 29.930 para el escalón. La ventana reciente conserva las previsiones puntuales anteriores. |
| Monografías | Regresión lineal, 2016–2025 | Menor MAE y RMSE medios que la tendencia logarítmica en la validación comparada. El salto de 2024 se mantiene como señal por investigar. |
| Personas por puesto | Media móvil, 2016–2025 | Ligera ventaja en MAE y RMSE sobre la alternativa logarítmica y el ingenuo. Las oscilaciones de 2021 y 2022 sugieren cautela sobre un cambio estable. |
| Gasto electrónico | Último observado con innovaciones logit, 2016–2025 | Error casi coincidente con el suavizado simple, con menos parámetros y un dominio acotado por construcción. |

Localizadores por indicador: `ajuste-publicado.csv`, `revision-candidatos.csv`, `revision-errores.csv`, `revision-metricas.csv`, `revision-escenarios.csv` y `diagnostico-serie.csv`. El [anexo revisado](#metodología-predictiva-revisada--25112026) conserva cifras, ventanas, comparación del cambio de nivel en 2020 y la comparación de pronósticos e intervalos anteriores y vigentes.

## 8. Incertidumbre estadística

Un intervalo de confianza para la media cuantifica la incertidumbre sobre la media esperada. Un intervalo de predicción para una observación nueva incorpora además la variabilidad de esa observación. El prototipo representa intervalos **marginales anuales del 95 % nominal**. Ese nivel se refiere a cada año bajo el modelo y sus supuestos. La cobertura simultánea de todos los años es otra propiedad y la muestra disponible no permite afirmar que la cobertura real alcance el nivel nominal.

| Indicador | Procedimiento vigente |
|---|---|
| Monografías | t de Student para una nueva observación en regresión lineal. Incluye dispersión residual y estimación de intercepto y pendiente. |
| Personas por puesto | Varianza residual a un paso e innovaciones aditivas propagadas por la media móvil de coeficientes fijos. |
| Gasto electrónico | Paseo aleatorio sin deriva en escala logit, con dispersión estimada a partir de diferencias. La transformación inversa de ambos extremos preserva 0–100 %. |
| Préstamos | Intervalo retirado. La ventana 2022–2025 aporta una sola innovación a un paso. La dispersión de toda la serie también recoge el salto de nivel y la recuperación. |

Los intervalos se calculan sin márgenes porcentuales arbitrarios. Se respetan los límites naturales de las variables y se registra cuando el procedimiento carece de datos suficientes, varianza positiva o un modelo de error implementado. La retirada del intervalo de préstamos evita dar una precisión aparente. La incertidumbre permanece. [Implementación](intervalos.py) · [Hyndman y Athanasopoulos, cap. 5 y 13](https://otexts.com/fpp3/)

El contraste por horizonte registra casos disponibles, estimables y cubiertos. A cinco pasos hay un caso estimable para monografías y uno para gasto. Los dos quedaron cubiertos. Para personas por puesto y préstamos no hay intervalo retrospectivo estimable a ese plazo. Las observaciones objetivo se solapan y los mismos años informan la selección de modelos, por lo que esta evidencia es exploratoria. Localizadores: `validacion-intervalos.csv`, `cobertura-intervalos.csv` y `serie-5.csv`; véanse [evidencias y limitaciones](#metodología-predictiva-revisada--25112026).

## 9. Estándar de representación gráfica

| Elemento | Representación implementada |
|---|---|
| Resultado BUS | Barra roja `#C8102E`, de anchura 0,36 unidades de año. |
| Límite | Barra morada `#512060`, de anchura 0,18. En prospectiva se usa solo el contorno de 1,1 pt. |
| Meta | Barra verde `#388E3C`, de anchura 0,18. En prospectiva se usa solo el contorno de 1,1 pt. |
| Previsión BUS | Barra de anchura 0,36 con fondo rosa `#F8D6DC`, rayado rojo y contorno de 1,1 pt. |
| Benchmark | Línea azul `#4682B4`, discontinua, de 1,1 pt. Círculo blanco de 4 pt con borde del color de la línea de 0,85 pt. |
| Referencia del grupo | Línea azul oscuro `#163D70`, continua, de 1,1 pt. Círculo blanco del mismo tamaño y contorno de su línea. |
| Liderazgo BUS | Círculo de referencia con relleno `#C8102E` y contorno `#163D70`. |
| Banda comparativa | Sombreado `#D6E7F5`, opacidad 0,53, sin borde. |
| Intervalo de predicción | Segmento vertical con remates horizontales `#3D4751`, de 0,8 pt. |
| Estimación puntual futura | Círculo blanco de 4 pt con contorno gris `#3D4751` de 0,85 pt. |

Las barras se ordenan de izquierda a derecha como límite, BUS y meta. La relación de anchuras **1:2:1** y el orden fijo facilitan localizar el resultado y compararlo con sus umbrales. La separación entre barras visibles de un mismo año es 0,03 unidades de año. Al ocultar una barra, la agrupación restante se recentra. Los periodos tienen rótulos propios y una divisoria vertical gris `#AEBAC8`. El rayado de la previsión y los contornos de la planificación futura permiten distinguirlos también por forma. La adaptación de la notación de escenarios al rojo, morado y verde del prototipo es una decisión del proyecto. [Parámetros](grafico.py) · [Reagrupamiento](selector.js) · [IBCS, escenarios visuales](https://www.ibcs.com/resource/top-and-bottom-5-of-international-business-communication-standards/)

El orden, de fondo a frente, es cuadrícula, banda, barras, líneas y marcadores comparativos, intervalos y marcadores puntuales futuros, y etiquetas. Los puntos circulares identifican el dato anual en las líneas de comparación. No se añaden líneas de tendencia. La posición de las referencias se calcula exclusivamente con las observaciones históricas. [Capas y estilos](grafico.py)

El eje vertical es lineal y empieza en cero para que la longitud de la barra sea proporcional al valor. El gasto se dibuja en 0–100 %. Para el resto, el techo se calcula con margen sobre el mayor dato representable de la vista. Ocultar elementos mantiene la escala de esa vista. El techo puede cambiar al alternar horizontes. La unidad figura en la lámina. Se usa punto para separar miles y coma para los decimales. Los recuentos BUS se rotulan sin decimales, personas por puesto con dos y gasto electrónico con uno y signo de porcentaje. Las cifras comparativas de recuentos pueden mostrar la fracción de la mediana. La precisión completa se conserva en los CSV. [Reglas de escala](grafico.py) · [Precisión por indicador](indicadores.json) · [ONS, ejes y cuadrícula](https://service-manual.ons.gov.uk/data-visualisation/guidance/axes-and-gridlines)

El fondo es blanco y la cuadrícula horizontal es gris claro `#DFE5EC`, de 0,65 pt. Los rótulos de la BUS tienen prioridad y 9,5 pt, frente a 7,5 pt en meta y límite. Dentro de la barra histórica la cifra es blanca y carece de recuadro. En el futuro conserva el color de la serie y la cifra BUS usa un fondo rosa claro `#FBE7EA` para separarse del rayado. En el exterior se usa fondo claro y, donde procede, un tono oscuro de la serie (rojo `#9B1025` o verde `#216528` en la vista web). Las pruebas de lectura realizadas son visuales y funcionales. La conformidad formal de accesibilidad y la legibilidad en la plataforma de evaluación siguen por comprobar. [Trazado](grafico.py) · [Colocación en la interfaz](selector.js) · [Renderizado inicial](etiquetas.py)

El algoritmo mide cajas de texto y segmentos en coordenadas de pantalla. Coloca primero la BUS, prueba posiciones verticales cerca del extremo de cada barra, desplaza las cifras para dejar espacio a marcas y trazos y busca una posición exterior si la barra es baja. Se calcula de nuevo al cambiar indicador, horizonte, visibilidad y tamaño, y antes de rasterizar el PNG. En configuraciones de saturación extrema, la implementación puede conservar la posición inicial si no encuentra una caja libre. Es un punto de revisión para indicadores futuros. [Algoritmo](colocacion.js) · [Pruebas geométricas](test_colocacion.js)

Las dos filas inferiores alinean las cifras con cada año. En el histórico se pueden activar Benchmark y Referencia. En prospectiva aparecen `IP inf.` e `IP sup.` cuando el intervalo es estimable y está visible. Se retiró la fila «Banda» porque repetía valores ya representados. Un extremo inexistente queda ausente. [Filas y controles](grafico.py) · [Actualización de visibilidad](selector.js)

## 10. Interactividad y exportación

El desplegable muestra una lámina cada vez. El cambio de indicador u horizonte conserva la selección de elementos y cifras. Los controles separan histórico, comparación externa y prospectiva. Se pueden alternar series y etiquetas asociadas, además del intervalo cuando existe. La leyenda refleja la selección y reúne las entradas de meta y límite de ambos periodos. «Restablecer selección» recupera la configuración inicial de visibilidad. [Interfaz](pagina.html) · [Lógica de selección](selector.js)

El PNG personalizado rasteriza el SVG con la selección activa y la colocación calculada a escala de **3.200 × 1.480 píxeles**. Incluye la lámina, la leyenda y las notas pertinentes. Los selectores son instrumentos de prueba y quedan fuera de la imagen. Cada vista dispone también de PNG y SVG iniciales y CSV reproducibles. La lectura de la imagen definitiva debe revisarse al tamaño real de la plataforma. [Exportación](selector.js) · [Generación estática](generar.py)

## 11. Validación del modelo gráfico

| Caso | Aspectos que permite validar |
|---|---|
| Préstamos domiciliarios | Trayectoria predominantemente decreciente, ruptura observada en 2020, ventana de ajuste distinta del histórico y ausencia explícita de intervalo estimable. |
| Monografías electrónicas de pago | Recuento creciente, escala de valores grandes, liderazgo respecto al conjunto e intervalo de regresión. La BUS fija la referencia de 2020 a 2025. Localizador: `NMONPAGOLIC/serie.csv`, campos `bus`, `referencia` y `bus_lider`. |
| Personas usuarias por puesto | Razón con dos decimales, polaridad decreciente, meta por debajo del límite e intervalo de media móvil. |
| Porcentaje del gasto electrónico | Escala acotada a 0–100 %, incertidumbre asimétrica en escala original y un extremo descriptivo con polaridad pendiente. |

**Cálculos.** Se contrastaron los valores observados y los agregados de los cuatro indicadores con los CSV originales. Las pruebas incluyen denominadores ausentes o nulos, polaridad decreciente, empates, coincidencia de años comunes a los horizontes y el contraste del intervalo lineal con la predicción para una nueva observación. [Pruebas estadísticas](test_indicadores.py) · [Resultados reproducibles](#anexo-técnico-y-resultados-reproducibles)

**Interacción.** Se comprobaron en navegador los cambios de indicador y horizonte, la conservación de la selección, la actualización de leyendas y filas, el redimensionado y la exportación. La colocación tiene pruebas específicas con cero, barras bajas, referencias concentradas e intervalos amplios. [Pruebas de colocación](test_colocacion.js) · [Validación publicada](https://github.com/mvarort/bus-indicadores-efqm/actions/runs/45678539490)

**Revisión visual y límites.** Se revisaron los cuatro PNG a escala reducida y con distintas selecciones. Quedan pendientes la revisión al tamaño real de la plataforma, la validación estratégica de indicadores y valores de gestión, la comprobación de definiciones entre campañas y la recalibración de los intervalos al incorporar nuevas observaciones. La inspección en un navegador y con casos de prueba aporta evidencia de funcionamiento para esas configuraciones.

## 12. Referencias bibliográficas y normativas

Se distingue el alcance normativo de las fichas de norma, el marco EFQM de evaluación, las recomendaciones y prácticas de referencia, y las decisiones propias documentadas en el registro. Las fichas públicas de UNE e ISO permiten verificar títulos y alcance general. La conformidad con cláusulas concretas, la aplicabilidad al expediente y la versión EFQM de 2028 requieren contraste específico con la documentación oficial.

| Fuente original | Alcance verificado y aplicación |
|---|---|
| EFQM. [*The EFQM Model*](https://efqm.org/the-efqm-model/), apartado «Results», y [*EFQM Global Award 2024 Recognition Book*](https://efqm.org/wp-content/uploads/2024/06/Recognition-Book-2024.pdf), prólogo sobre la presentación del Modelo 2025. | Marco de evaluación. Su página pública vincula resultados alcanzados y futuros. El proyecto usa 2025 como referencia de trabajo. La edición aplicable a 2028 y los requisitos de presentación deben confirmarse. La regla de una imagen se recoge como condición del encargo, a falta de comprobación para la convocatoria. Los colores, la cantidad de años y los comparadores son decisiones del prototipo. |
| UNE 66175:2003. [*Sistemas de gestión de la calidad. Guía para la implantación de sistemas de indicadores*](https://tienda.aenor.com/p/norma-une-66175-2003-n0030150), 31/10/2003, confirmación 18/11/2010. | Guía técnica. Orienta la formalización de indicadores, definiciones y seguimiento. La ficha confirma identificación, título y fechas. |
| ISO 11620:2023. [*Information and documentation — Library performance indicators*](https://www.iso.org/standard/83126.html), 4.ª ed., junio de 2023, resumen y alcance. | Norma técnica de indicadores bibliotecarios. Sirve para contrastar terminología, aplicabilidad, recogida y análisis cuando se formalicen las fichas. |
| ISO 2789:2022. [*Information and documentation — International library statistics*](https://www.iso.org/standard/78525.html), 6.ª ed., septiembre de 2022, resumen y alcance. | Norma técnica de recogida y presentación de estadísticas bibliotecarias. Fundamenta la comprobación de comparabilidad de definiciones y unidades. |
| REBIUN. [*Estadísticas*](https://www.rebiun.org/grupos-trabajo/estadisticas), formulario y anuarios anuales. | Fuente institucional de procedencia y de definiciones de campaña. Se consulta para distinguir una variación real de una revisión de registro. |
| REBIUN Data Explorer. [Aplicación pública](https://mvarort.github.io/datos-rebiun/) y [revisión fijada de los CSV](https://github.com/mvarort/datos-rebiun/tree/25996fc11eb8212e11a114b58884b3741c6194bd/data). | Fuente de acceso y tratamiento reproducible. Identifica la instantánea, los códigos y los datos empleados en el prototipo. |
| IBCS Association. [*IBCS Version 2.0*](https://www.ibcs.com/ibcs-version-2-0/), publicada el 11/06/2026, y [*Top and bottom 5 of International Business Communication Standards*](https://www.ibcs.com/resource/top-and-bottom-5-of-international-business-communication-standards/), «Scenarios». | Referencia de notación visual de escenarios. Inspira el uso de relleno, rayado y contorno. Se usa como buena práctica, sin atribuir conformidad con IBCS ni con ISO 24896. |
| Office for National Statistics. [*Chart details: Axes and gridlines*](https://service-manual.ons.gov.uk/data-visualisation/guidance/axes-and-gridlines), «Axis start point», «Axis end point» y «Gridlines». | Guía pública de visualización. Fundamenta la escala desde cero en barras y la cuadrícula subordinada al dato. |
| Hyndman, R. J. y Athanasopoulos, G. (2021). [*Forecasting: Principles and Practice*, 3.ª ed.](https://otexts.com/fpp3/), capítulos [5](https://otexts.com/fpp3/toolbox.html), [7](https://otexts.com/fpp3/regression.html), [8](https://otexts.com/fpp3/ets-forecasting.html) y [13](https://otexts.com/fpp3/practical.html). | Referencia metodológica para validación temporal, predicción de una observación futura, intervención escalón, suavizado, restricciones naturales y series cortas. |
| APQC. [*How Can KPI Definitions Support Valid Comparison?*](https://www.apqc.org/How-Can-KPI-Definitions-Support-Valid-Comparison), normalización y metodología en cuatro fases. | Buena práctica para definir pares, validar la información, analizar y adaptar prácticas. No fija la mediana ni el umbral de 40.000 del prototipo. |
| IBM. [*Benchmarking — IBM Apptio*](https://www.ibm.com/products/apptio/benchmarking), «Understand how you compare to self-selected peers» y «Justify current IT expense and defend budgets». | Ejemplo de producto que contrasta resultados con pares y muestra extremos mediante diagramas de caja. Es un referente conceptual de comparación. La banda mediana–extremo del prototipo tiene otra definición. |
| Illowsky, B. y Dean, S. (2023). [*Introductory Statistics 2e*](https://openstax.org/books/introductory-statistics-2e/pages/1-introduction), OpenStax, [§2.3](https://openstax.org/books/introductory-statistics-2e/pages/2-3-measures-of-the-location-of-the-data) y [§2.5](https://openstax.org/books/introductory-statistics-2e/pages/2-5-measures-of-the-center-of-the-data). | Referencia estadística para mediana, sensibilidad de la media y diferencia entre una banda descriptiva y el rango intercuartílico. |

## 13. Registro de decisiones

La fecha indica la consolidación documental. «Consolidada» significa implementada y contrastada en el prototipo. «Provisional» indica que se usa para ensayar el modelo y «Pendiente de validación» requiere una comprobación o acuerdo adicional.

| Identificador | Decisión | Justificación | Alternativas consideradas o descartadas | Fuente | Estado | Fecha |
|---|---|---|---|---|---|---|
| MR-01 | Lámina individual y autosuficiente | Lectura en el expediente y comparación de configuraciones | Cuadro de mando con varias gráficas simultáneas | Encargo y [exportación](selector.js) | Consolidada | 25/11/2026 |
| MR-02 | Revisión fija y cálculo por biblioteca y año | Reproducibilidad y control de definiciones | Actualización silenciosa o razones de totales | REBIUN y [tratamiento](datos.py) | Consolidada | 25/11/2026 |
| MR-03 | Diez años visibles y prospectiva de tres o cinco con ajuste común | Mostrar evolución y mantener cifras comunes | Ajustar un modelo por horizonte o recortar el histórico mostrado | [Configuración](indicadores.json) y [generación](generar.py) | Consolidada | 25/11/2026 |
| MR-04 | Comparadores presenciales con más de 40.000 usuarios, elegibilidad anual y mediana externa | Afinidad de población y robustez a extremos | Media simple, grupo fijo o incluir a la BUS en el centro de comparación | OpenStax, APQC y [cálculo](datos.py) | Consolidada | 25/11/2026 |
| MR-05 | Extremo con BUS, máximo o mínimo, y marcador de liderazgo con empates | Mostrar el mayor o menor resultado real del conjunto evaluado | Extremo solo externo o señalar solo victorias estrictas | [Cálculo](datos.py) y [marcador](grafico.py) | Consolidada | 25/11/2026 |
| MR-06 | Banda mediana–extremo | Ubicar el resultado entre dos referencias legibles | Superficies separadas y sombreado desde cero | [Modelo gráfico](grafico.py), OpenStax y contraste con IBM Apptio | Consolidada | 25/11/2026 |
| MR-07 | Máximo descriptivo para gasto electrónico | La polaridad estratégica requiere acuerdo | Interpretar automáticamente que gastar una proporción mayor es mejor | [Configuración](indicadores.json) | Provisional | 25/11/2026 |
| MR-08 | Metas y límites ilustrativos independientes de la previsión | Ensayar la lámina sin convertir resultados estadísticos en compromisos | Usar directamente los extremos predictivos como umbrales | [Configuración](indicadores.json), UNE 66175 como guía | Provisional | 25/11/2026 |
| MR-09 | Elegir método con orígenes expansivos y MAE/RMSE comparables | Reducir sesgo de evaluación y limitar complejidad | Comparar ventanas sobre objetivos distintos o elegir por estrechez del intervalo | FPP3 y [anexo](#metodología-predictiva-revisada--25112026) | Consolidada | 25/11/2026 |
| MR-10 | Media móvil reciente para préstamos sin intervalo publicado | Resultado puntual estable y una sola innovación reciente | Serie completa para la dispersión, escalón como pronóstico publicado o margen arbitrario | [Anexo predictivo](#metodología-predictiva-revisada--25112026) y [cálculo](intervalos.py) | Consolidada | 25/11/2026 |
| MR-11 | Intervalos marginales nominales en las otras tres series | Representar variabilidad futura condicionada al modelo | Intervalos de confianza de la media o cobertura conjunta supuesta | FPP3 y [cálculo](intervalos.py) | Provisional | 25/11/2026 |
| MR-12 | Jerarquía de barras, capas y etiquetas adaptativas | Mantener el foco en BUS y reducir interferencias | Anchuras uniformes, etiquetas fijas, filas duplicadas y líneas de tendencia | ONS, IBCS y [pruebas](test_colocacion.js) | Consolidada | 25/11/2026 |
| MR-13 | Selección experimental y exportación PNG sin controles | Evaluar variantes y obtener imagen de evaluación | Captura de la interfaz completa | [Exportación](selector.js) | Consolidada | 25/11/2026 |
| MR-14 | Confirmar edición EFQM, selección definitiva y condiciones de presentación | Aplicar los requisitos vigentes del ciclo | Presuponer continuidad desde 2025 | EFQM y alcance del encargo | Pendiente de validación | 25/11/2026 |
| MR-15 | Contrastar definiciones de campaña y calibrar con más observaciones | Interpretar rupturas y mejorar evidencia de cobertura | Atribuir causalidad o cobertura a la muestra actual | REBIUN, ISO y [anexo predictivo](#metodología-predictiva-revisada--25112026) | Pendiente de validación | 25/11/2026 |
| MR-16 | Ventana histórica inclusiva independiente del ajuste y de la prospectiva | Permite centrar la lectura en un periodo con comparaciones constantes y evitar saltos si se recorta el último año | Reestimar con la ventana visible o mostrar prospectiva tras un histórico discontinuo | [Generación](generar.py), [controles](selector.js) y [pruebas](test_indicadores.py) | Consolidada | 26/11/2026 |

## 14. Mantenimiento y publicación

1. Identificar y archivar la campaña y su revisión. Contrastar unidades, población, definiciones y posibles correcciones con los formularios de REBIUN.
2. Revisar alertas de datos, integrantes del comparador y fórmulas. Regenerar y conservar la instantánea derivada con su procedencia.
3. Repetir el contraste predictivo, registrar el periodo y el modelo elegidos, y revisar la posibilidad de estimar y calibrar los intervalos. Las metas y los límites oficiales requieren una decisión de gestión.
4. Ejecutar las pruebas estadísticas y de colocación, revisar ambas vistas y los PNG en sus tamaños de lectura y actualizar el registro de decisiones. Documentar con fecha las discrepancias o condiciones pendientes.
5. Publicar la revisión junto a sus datos reproducibles. GitHub es la edición de referencia. La copia estática que genera Pages conserva el texto, pero algunos enlaces relativos a código y configuración requieren consultar el repositorio. La revisión de esos vínculos queda pendiente para una actualización técnica. [Instrucciones de generación y publicación](README.md) · [Flujo de GitHub Actions](.github/workflows/pages.yml)

## Anexo técnico y resultados reproducibles

Se conservan a continuación la evidencia técnica, los pronósticos de referencia y los de la revisión predictiva. Las secciones identificadas como referencia anterior describen el punto de comparación histórico. Para las cifras vigentes, úsense `ajuste-publicado.csv`, `serie.csv` y `serie-5.csv` de cada indicador.

## Préstamos domiciliarios · NPRESTDOMIC

Fuente REBIUN Data Explorer, revisión `25996fc11eb8212e11a114b58884b3741c6194bd`.
En el CSV longitudinal, las claves son año, código de biblioteca y código técnico.
Para la BUS se usa 67, según el directorio. Se conserva el código técnico NPRESTDOMIC
a lo largo de 2016–2025. El rótulo publicado cambia desde 2022 y el código REBIUN
de apartado pasa a 6.2.1 en 2023. La equivalencia de definiciones de campaña
queda pendiente de confirmación documental. [CSV originales](https://github.com/mvarort/datos-rebiun/tree/25996fc11eb8212e11a114b58884b3741c6194bd/data).

El directorio aporta una modalidad por centro, aplicada a todo el periodo.
Cada año se filtran centros presenciales distintos de 67 que declaren
NUSUARIOPROP superior a 40.000. Se mantienen en el listado los elegibles sin
NPRESTDOMIC, si los hay. El Benchmark es la mediana de los valores externos
disponibles. La Referencia del grupo incorpora también el valor de la BUS.
Se incluye el cero cuando figura como dato válido. Los comparadores
empatados en la referencia se identifican en `grupo.csv`. Son recuentos absolutos. La composición
variable y la escala de los centros condicionan la comparación.

## Ruptura alrededor de 2020

La BUS pasa de 562.570 préstamos en 2019 a 300.264 en 2020 (−46,6 %) y
279.470 en 2021. En 2025 registra 350.602. El patrón coincide temporalmente
con la pandemia y sugiere un cambio de nivel. La serie anual por sí sola
no identifica cuánto del descenso se debió a la pandemia ni qué otros
factores influyeron. Fuente: `data/rebiun_real.csv`, BUS 67, NPRESTDOMIC,
2019–2021 y 2025, revisión citada.

Los modelos se comparan sobre la serie completa para que compartan orígenes
y conserven la ruptura en los datos. Se requieren cinco datos para el
primer ajuste, por lo que el primer origen es 2020. Los errores miden
la capacidad de anticipar resultados posteriores desde ese punto, incluida
la recuperación. El método ganador usa solo los tres últimos años en cada
origen y, en el ajuste final, solo 2023–2025. Por ello, ajustar el ganador
a 2022–2025 produce la misma previsión que ajustar a 2016–2025. Un ajuste
a la etapa reciente para los cinco métodos dejaría demasiado pocos datos
para comparar en condiciones equivalentes.

## Metodología de referencia anterior · préstamos

Se contrastan el último observado, la media móvil recursiva de tres años,
una regresión lineal con intercepto, el suavizado exponencial simple
optimizado y Holt con tendencia amortiguada optimizada. Todos usan
ventana de entrenamiento expansiva hasta el origen, con horizontes de
uno a tres años y recorte de valores negativos a cero. El recorte refleja
la naturaleza del indicador. Los errores usan predicciones sin redondear.
Los valores de la gráfica y la serie CSV están redondeados al préstamo.

Los orígenes van de 2020 a 2024. Hay 5 errores a un año, 4 a dos años y
3 a tres años por método. MAE es la media del error absoluto y RMSE es
la raíz del error cuadrático medio. En la metodología de referencia se elige el menor promedio de los
tres MAE por horizonte. En un empate, se usa el promedio de los RMSE.
Cada horizonte recibe igual peso.

| Modelo | MAE medio | RMSE medio |
|---|---:|---:|
| Media móvil de 3 años | 44.090 | 57.046 |
| Suavizado exponencial simple | 55.934 | 64.697 |
| Ingenuo | 61.999 | 71.704 |
| Holt con tendencia amortiguada | 126.593 | 167.771 |
| Regresión lineal | 178.245 | 185.750 |

Localizador de los cálculos: [selección](datos_procesados/seleccion.csv),
[métricas por horizonte](datos_procesados/validacion.csv) y
[errores por origen](datos_procesados/errores-validacion.csv).

El modelo seleccionado estima 365.118, 348.660 y 354.793 préstamos para
2026, 2027 y 2028 respectivamente. Selección y evaluación usan los mismos
orígenes. El ranking es exploratorio y los errores comparten años
objetivo. Entre tres y cinco errores por horizonte, junto con el cambio
de nivel histórico, impiden calibrar la cobertura con fiabilidad.
Los intervalos del apartado de prospectiva son nominales y dependen
de sus supuestos estadísticos. Mediana y referencia del grupo se muestran solo en el histórico.
Las metas y límites de 2016–2030 están en la configuración y son
ilustrativos. En la lámina, la línea azul media sigue la mediana y la
azul oscura, el mejor resultado. La banda semitransparente ocupa el espacio
entre ambas líneas y termina en el último año observado. Para indicadores de
polaridad decreciente (`mejor: min`), la referencia es el mínimo
anual y el área queda entre ese mínimo y la mediana. Para los de
polaridad creciente (`mejor: max`), el máximo es la referencia.
Cuando la BUS alcanza el extremo con polaridad definida, incluidos
los empates, el círculo de la referencia se rellena de rojo. La
columna `bus_lider` recoge esa condición en `serie.csv`.
La banda describe resultados observados del grupo, sin interpretación
de intervalo de confianza ni de zona de excelencia. El PNG integra estas definiciones, la nota de
incertidumbre y las cifras BUS en vertical dentro de sus barras. Los
valores exactos de metas, límites y comparaciones están en el CSV.

## Referencias de trabajo

UNE 66175 orienta la definición y seguimiento de indicadores. ISO 11620
sirve de referencia terminológica para indicadores bibliotecarios e
ISO 2789 para estadísticas bibliotecarias. EFQM 2025 sitúa el prototipo
en el trabajo sobre resultados. La versión aplicable a 2028 queda por
confirmar. La distinción gráfica entre observación, previsión y
planificación se inspira en IBCS. Las guías de ONS orientan la
legibilidad de escalas, etiquetas y cuadrículas. Los colores, anchuras
y el comparador son decisiones del prototipo.
[UNE](https://www.une.org/), [ISO 11620](https://www.iso.org/standard/83126.html),
[ISO 2789](https://www.iso.org/standard/78525.html),
[EFQM](https://efqm.org/the-efqm-model/),
[IBCS](https://www.ibcs.com/standards/),
[ONS](https://service-manual.ons.gov.uk/data-visualisation).

## Ampliación a cuatro indicadores

La revisión de FU-010 indicada arriba contiene, para BUS 67 y
2016–2025, diez valores anuales de cada variable necesaria. Localizador:
`data/rebiun_real.csv`, claves `Anio`, `Codigo_Biblioteca_REBIUN` y
`Codigo_Tecnico`. Las definiciones de esta tabla son las denominaciones
del fichero longitudinal. Las razones son cálculos del prototipo.

| Indicador | Cálculo | Referencia anual (incluida la BUS) |
|---|---|---|
| Préstamos domiciliarios de material bibliográfico | `NPRESTDOMIC`, préstamos domiciliarios | Máximo |
| Monografías electrónicas de pago | `NMONPAGOLIC`, recuento de monografías electrónicas de pago | Máximo |
| Personas usuarias por puesto de lectura | `NUSUARIOPROP` (personas usuarias propias) / `NPUESTOSLECT` (puestos de lectura) | Mínimo |
| Porcentaje del gasto en información electrónica | 100 × `GASTOINFOELECT` (gasto en información electrónica) / `GASTORECINFO` (gasto en recursos de información) | Máximo descriptivo provisional |

La polaridad estratégica del porcentaje queda pendiente. El máximo que incluye a la BUS es descriptivo y no genera marcadores de liderazgo. Sus metas y
límites ilustrativos son referencias gráficas, sin valoración del
desempeño. Para puestos de lectura, la meta es inferior al límite por
tratarse de una razón de polaridad decreciente.

Se calcula cada razón por biblioteca y año antes de obtener la mediana
y el extremo del grupo. Si falta un componente, el denominador es cero
o el resultado queda fuera del dominio natural, ese resultado se
considera ausente. El centro elegible permanece en el fichero del grupo
y queda fuera de las estadísticas del indicador del año. En esta
revisión hay 96 registros comparadores elegibles con resultado válido
para cada serie nueva, sumando los diez años. Localizador: `grupo.csv`
y campos `elegibles` y `con_dato` de cada `serie.csv`.

La misma validación temporal se aplica por separado a cada serie, con
los cinco modelos y la prioridad MAE/RMSE descritos arriba. Se limita
cada pronóstico de validación y final al dominio natural del indicador.
Los porcentajes se acotan a 0–100. El ajuste utiliza la escala numérica
declarada en la configuración. El CSV conserva las cifras históricas
y los agregados con su precisión de cálculo. Las previsiones puntuales
se redondean a la precisión de la lámina. Las métricas y errores se
pueden auditar por origen y horizonte en los CSV de cada indicador.

| Indicador | Método elegido | MAE medio | RMSE medio | 2026 | 2027 | 2028 |
|---|---|---:|---:|---:|---:|---:|
| Préstamos | Media móvil de 3 años | 44.090 | 57.046 | 365.118 | 348.660 | 354.793 |
| Monografías de pago | Regresión lineal | 63.070 | 73.730 | 1.090.553 | 1.149.525 | 1.208.497 |
| Personas usuarias por puesto | Media móvil de 3 años | 0,55 | 0,64 | 10,77 | 10,91 | 10,89 |
| Gasto electrónico | Suavizado exponencial simple | 1,04 pp | 1,18 pp | 89,0 % | 89,0 % | 89,0 % |

Localizadores: `seleccion.csv` para el contraste de referencia y `ajuste-publicado.csv` para el modelo vigente en cada carpeta.
La muestra de validación sigue siendo breve. Las previsiones sirven
para probar la representación y conservan la advertencia de
incertidumbre. La calibración de la cobertura queda pendiente.

En las monografías electrónicas de pago, la BUS fija la referencia
anual en 2020–2025. En 2025 la referencia coincide con su resultado,
1.024.655. El mayor valor de los comparadores externos es 946.714.
Localizadores: `NMONPAGOLIC/serie.csv`, campos `bus`, `referencia` y
`bus_lider`, y `NMONPAGOLIC/grupo.csv`, valores del indicador en 2025.

## Prospectiva a tres y cinco años · referencia anterior

La selección del método usa el mismo ranking temporal de uno a tres
años descrito arriba. Se ajusta el modelo elegido una sola vez para los
cinco años y la vista de tres años muestra el prefijo 2026–2028.
Las metas y límites de 2029–2030 son ilustrativos.

Los intervalos son **marginales por año**, de nivel nominal del 95 %.
Representan un nuevo resultado anual bajo el modelo y utilizan
cuantiles de t de Student. Se calculan sobre las previsiones sin
redondear y se acotan a los límites naturales del indicador.
Los remates grises representan los extremos predictivos. Las barras
moradas representan los límites ilustrativos de gestión.

- **Monografías · regresión lineal.** Intervalo para una nueva
  observación con error residual y extrapolación de los coeficientes:
  error estándar residual multiplicado por la raíz de
  `1 + 1/n + (x_f − media(x))² / Sxx`, con `n − 2` grados de libertad.
  Supone errores independientes, normales y de varianza constante.
- **Préstamos y personas por puesto · media móvil de tres años.**
  Se explicita un modelo condicional con coeficientes fijos de 1/3
  y una innovación aditiva independiente en cada año. La varianza se
  estima con los errores de predicción a un paso de los años con tres
  antecedentes. Se propagan las innovaciones por la misma recursión
  de la previsión puntual. Con diez datos hay siete innovaciones.
- **Gasto electrónico · suavizado exponencial simple.** Se usa el
  modelo de nivel con innovaciones aditivas. La varianza a horizonte
  `h` es la varianza residual multiplicada por
  `1 + (h − 1) × alfa²`. Se usa `n − 2` como ajuste aproximado por
  estimar nivel y alfa. El cálculo condiciona la propagación al alfa
  ajustado y deja fuera su incertidumbre de estimación.

Los supuestos pueden fallar ante cambios de nivel, como el observado en
préstamos, o ante dependencia temporal. El procedimiento no incorpora
la incertidumbre de seleccionar el modelo ni promete cobertura simultánea.
Si faltan tres grados de libertad, la varianza residual no es positiva
o el modelo elegido carece de un método implementado, se deja el
intervalo sin estimar.

Se evaluó el modelo elegido con orígenes expansivos y sin usar los
datos posteriores a cada origen para ajustar el intervalo. Los mismos
años informaron la elección previa del modelo. Esta cobertura es
exploratoria, con observaciones objetivo solapadas y como máximo
un caso a cinco años.

| Indicador | 1 año | 2 años | 3 años | 4 años | 5 años |
|---|---:|---:|---:|---:|---:|
| Préstamos | 4/4 | 3/3 | 2/2 | 1/1 | — |
| Monografías | 4/5 | 4/4 | 3/3 | 2/2 | 1/1 |
| Personas por puesto | 4/4 | 3/3 | 2/2 | 1/1 | — |
| Gasto electrónico | 5/5 | 4/4 | 3/3 | 2/2 | 1/1 |

Celdas: resultados observados cubiertos / intervalos estimables. El
guion indica que ningún intervalo retrospectivo fue estimable en ese
horizonte. En la metodología anterior, el ajuste con diez años producía intervalos nominales para los cuatro indicadores hasta 2030. Los CSV
`validacion-intervalos.csv` y `cobertura-intervalos.csv` incluyen
el detalle por origen y el resumen por plazo. `serie.csv` y
`serie-5.csv` incluyen `prediccion_inferior_95` y
`prediccion_superior_95`, diferenciados de la columna `limite`.

Para el modelo de nivel, la expresión de la varianza sigue el modelo
ETS(A,N,N) de [Hyndman y Athanasopoulos, §8.7](https://otexts.robjhyndman.com/fpp3/ets-forecasting.html).

## Metodología predictiva revisada · 25/11/2026

La lámina representa 2016–2025 íntegramente. La configuración interna
`prevision.inicio_ajuste` fija el primer año utilizado en la previsión
publicada. El horizonte largo y el corto comparten un ajuste. Las metas y
los límites ilustrativos se conservan y sus valores se mantienen
independientes de los extremos de predicción.

Se contrastan el último valor observado (ingenuo), media móvil de tres
años, regresión lineal, suavizado exponencial simple y Holt amortiguado.
La serie completa exige cinco años antes del primer origen. La ventana
reciente 2022–2025 exige dos datos para el ingenuo, tres para media móvil,
regresión y suavizado, y cinco para Holt. Por ello Holt reciente queda
sin estimar. Los errores se calculan desde orígenes expansivos y en las
unidades originales. Se publican MAE, RMSE y número de casos por plazo
hasta cinco años. Los grupos de validación son todos los orígenes
disponibles, el origen común 2024 y los orígenes 2022–2024. Para comparar
candidatos se usan los mismos orígenes y plazos. Cuando un escenario
carece de casos comunes adicionales, se conserva como sensibilidad.

### Préstamos domiciliarios

El salto de 2019 a 2020 fue de −262.306 préstamos (−46,6 %). El modelo de
intervención usa una regresión con intercepto e indicador escalón
desde 2020, sin pendiente. La fecha se fija por el cambio conocido
y la exploración es retrospectiva. Las medias ajustadas antes y después
son 585.451 y 339.918. El AICc de la regresión con escalón es 222,94
frente a 240,82 para una media constante, en ambos casos omitiendo la
misma constante gaussiana y contando la varianza como parámetro.
El contraste respalda estudiar un cambio de nivel. Con cuatro
observaciones previas y seis posteriores resulta insuficiente
para establecer su causa o permanencia.

| Comparación | Media móvil completa | Media móvil reciente | Cambio de nivel |
|---|---:|---:|---:|
| Origen común 2024, error absoluto a un año | 19.122 | 19.122 | 12.821 |
| Orígenes 2022–2024, MAE medio de 1–3 pasos | 27.844 | — | 29.930 |
| Orígenes 2022–2024, RMSE medio de 1–3 pasos | 32.697 | — | 35.885 |

Entre los métodos recientes con un solo caso común, suavizado y
regresión obtuvieron errores absolutos de 13.819 y 15.039. El ingenuo
obtuvo 20.342. El único caso común no permite establecer superioridad.
En los orígenes 2022–2024, la media móvil quedó por delante del cambio
de nivel, de los demás métodos de serie completa y de la alternativa
en logaritmos (MAE 28.150 y RMSE 33.329 para esta última). Se conserva
la media móvil aritmética por su desempeño comparativo y parsimonia.
Para el ajuste final se usa 2022–2025 (cuatro datos). Como la recursión
solo necesita los tres últimos, la estimación puntual coincide con la
anterior. Los valores se mantienen no negativos por construcción.

| Año | Previsión anterior | Previsión revisada | Intervalo anterior, nominal 95 % | Intervalo revisado |
|---|---:|---:|---:|---|
| 2026 | 365.118 | 365.118 | 56.901–673.335 | No estimable |
| 2027 | 348.660 | 348.660 | 23.771–673.549 | No estimable |
| 2028 | 354.793 | 354.793 | 2.206–707.381 | No estimable |
| 2029 | 356.190 | 356.190 | 0–753.277 | No estimable |
| 2030 | 353.214 | 353.214 | 0–774.522 | No estimable |

La ventana reciente deja una sola innovación observable para estimar
la dispersión a un paso. El único origen retrospectivo disponible
para la media móvil reciente tampoco permite ajustar un intervalo.
Se retiran los intervalos de la vista de préstamos y se deja constancia
en la lámina y en los CSV. Los intervalos anteriores mezclaban el
salto de nivel y la recuperación con la dispersión esperada del periodo
reciente. El escalón estima 339.918 para cada año futuro y se conserva
en `revision-escenarios.csv` como sensibilidad.

### Otros indicadores

Los cambios anuales se inspeccionan en `diagnostico-serie.csv`
y se compara la ventana completa con la reciente. La corta ventana
reciente deja como máximo un origen común con tres antecedentes.
Los cambios se interpretan como señales exploratorias.

- **Monografías.** El incremento de 2019 (+154.049) y el de 2024
  (+201.527), seguido de un descenso de 29.854 en 2025, aconsejan
  vigilar posibles cambios de adquisición o registro. La fuente
  estadística no identifica su causa. Se conserva la regresión
  lineal 2016–2025 (n=10), con MAE/RMSE medios 63.070/73.730 frente
  a 74.842/86.112 para la regresión logarítmica. Un escalón en 2024
  tendría solo dos observaciones posteriores. El intervalo de nueva
  observación incluye el error residual y la estimación del intercepto
  y la pendiente. Los extremos y previsiones vigentes están en
  `serie-5.csv`.
- **Personas por puesto.** La disminución de 2021 (−0,83) y el rebote
  de 2022 (+0,68) son cambios de signo opuesto. La media móvil de
  2016–2025 (n=10) obtiene MAE/RMSE 0,554/0,639 frente a
  0,559/0,643 en logaritmos y 0,561/0,666 del ingenuo. Se conserva
  la media móvil con su intervalo condicional de innovaciones
  aditivas. La escasa ventaja y el único caso a cuatro pasos
  requieren cautela.
- **Gasto electrónico.** Sube 3,38 puntos porcentuales en 2020,
  tras subir 2,71 en 2019. La evolución posterior no basta para
  estimar un nuevo régimen permanente. Se publica el último valor
  observado, modelado como paseo aleatorio sin deriva en escala
  logit, con 2016–2025 (n=10). A la precisión relevante, sus errores
  1,038/1,184 pp coinciden con los del suavizado simple. El ingenuo
  evita estimar un parámetro de suavizado. El pronóstico central
  es la mediana de la distribución transformada (89,0 % tras
  redondear). En la escala logit se usa la varianza de las nueve
  diferencias anuales, con factor de horizonte `h` y cuantil t.
  La transformación íntegra de los extremos garantiza 0–100 %.
  Así, el intervalo es aproximadamente 85,9–91,5 % en 2026 y
  81,0–93,9 % en 2030. La polaridad estratégica sigue pendiente.

Las cifras y los cambios proceden de FU-010, `data/rebiun_real.csv`,
código 67, variables y fórmulas descritas arriba. Los archivos
`ajuste-publicado.csv`, `revision-candidatos.csv`,
`revision-errores.csv`, `revision-metricas.csv` y
`revision-escenarios.csv` recogen ventana, tamaño de muestra,
pronósticos de sensibilidad y errores auditables. `serie-5.csv`
contiene las predicciones e intervalos publicados y
`cobertura-intervalos.csv` contiene el contraste retrospectivo
del modelo publicado. En los tres indicadores con intervalos,
a cinco pasos solo son estimables un caso para monografías y uno
para gasto, ambos cubiertos. El 95 % es nominal y la muestra no
permite calibrar la cobertura. Los intervalos son por año y
condicionados a las especificaciones elegidas. No incorporan
incertidumbre de selección o de cambios futuros de régimen.

Referencias: Hyndman y Athanasopoulos, *Forecasting: Principles and
Practice*, [validación temporal e intervalos](https://otexts.com/fpp3/toolbox.html),
[variables de intervención](https://otexts.com/fpp3/regression.html)
y [pronósticos con restricciones y series cortas](https://otexts.com/fpp3/practical.html).
