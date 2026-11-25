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

## Comparación de modelos

Se contrastan el último observado, la media móvil recursiva de tres años,
una regresión lineal con intercepto, el suavizado exponencial simple
optimizado y Holt con tendencia amortiguada optimizada. Todos usan
ventana de entrenamiento expansiva hasta el origen, con horizontes de
uno a tres años y recorte de valores negativos a cero. El recorte refleja
la naturaleza del indicador. Los errores usan predicciones sin redondear.
Los valores de la gráfica y la serie CSV están redondeados al préstamo.

Los orígenes van de 2020 a 2024. Hay 5 errores a un año, 4 a dos años y
3 a tres años por método. MAE es la media del error absoluto y RMSE es
la raíz del error cuadrático medio. Se elige el menor promedio de los
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

Localizadores: `seleccion.csv` y `serie.csv` en cada carpeta de indicador.
La muestra de validación sigue siendo breve. Las previsiones sirven
para probar la representación y conservan la advertencia de
incertidumbre. La calibración de la cobertura queda pendiente.

En las monografías electrónicas de pago, la BUS fija la referencia
anual en 2020–2025. En 2025 la referencia coincide con su resultado,
1.024.655. El mayor valor de los comparadores externos es 946.714.
Localizadores: `NMONPAGOLIC/serie.csv`, campos `bus`, `referencia` y
`bus_lider`, y `NMONPAGOLIC/grupo.csv`, valores del indicador en 2025.

## Prospectiva a tres y cinco años e incertidumbre

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
horizonte. El ajuste final, con diez años, sí produce intervalos
nominales para los cuatro indicadores hasta 2030. Los CSV
`validacion-intervalos.csv` y `cobertura-intervalos.csv` incluyen
el detalle por origen y el resumen por plazo. `serie.csv` y
`serie-5.csv` incluyen `prediccion_inferior_95` y
`prediccion_superior_95`, diferenciados de la columna `limite`.

Para el modelo de nivel, la expresión de la varianza sigue el modelo
ETS(A,N,N) de [Hyndman y Athanasopoulos, §8.7](https://otexts.robjhyndman.com/fpp3/ets-forecasting.html).
