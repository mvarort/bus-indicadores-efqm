# Metodología de los indicadores EFQM

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
