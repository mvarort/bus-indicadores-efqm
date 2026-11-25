# Metodología · NPRESTDOMIC

## Datos y comparación

Fuente REBIUN Data Explorer, revisión `25996fc11eb8212e11a114b58884b3741c6194bd`.
En el CSV longitudinal, las claves son año, código de biblioteca y código técnico.
Para la BUS se usa 67, según el directorio. Se conserva el código técnico NPRESTDOMIC
a lo largo de 2016–2025. El rótulo publicado cambia desde 2022 y el código REBIUN
de apartado pasa a 6.2.1 en 2023. La equivalencia de definiciones de campaña
queda pendiente de confirmación documental. [CSV originales](https://github.com/mvarort/datos-rebiun/tree/25996fc11eb8212e11a114b58884b3741c6194bd/data).

El directorio aporta una modalidad por centro, aplicada a todo el periodo.
Cada año se filtran centros presenciales distintos de 67 que declaren
NUSUARIOPROP superior a 40.000. Se mantienen en el listado los elegibles sin
NPRESTDOMIC, si los hay. Mediana y máximo usan observaciones disponibles,
incluido cero cuando figura como valor. Todos los centros empatados en el
máximo se marcan como referencia. Son recuentos absolutos. La composición
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
de nivel histórico, impiden calibrar con fiabilidad intervalos de
predicción empíricos. Se publican estimaciones puntuales con esta
limitación. Mediana y referencia del grupo se muestran solo en el histórico.
Las metas y límites de 2016–2028 están en la configuración y son
ilustrativos. En la lámina, la zona azul parte de cero y termina en la
mediana. La zona amarilla parte de la mediana y termina en el mejor
resultado anual. El PNG integra estas definiciones, la nota de
incertidumbre y las cifras para poder interpretarlo fuera de la web.

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
