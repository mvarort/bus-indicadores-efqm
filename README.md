# Indicadores BUS · EFQM 2028

Prototipo estático de préstamos domiciliarios basado en REBIUN Data Explorer.
[Aplicación](https://mvarort.github.io/bus-indicadores-efqm/) ·
[Metodología, resultados y limitaciones](metodologia.md).

## Instalación

Con Python 3.9:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python generar.py
python -m unittest -v
python -m http.server 8000 --directory site
```

Abre http://localhost:8000. El generador obtiene los CSV públicos de la
revisión declarada en `indicadores.json`. Para trabajar sin red, pásale
`--datos /ruta/a/data` apuntando al directorio con ambos CSV originales.

## Actualización

`datos.py` lee y cruza las fuentes, `prevision.py` ajusta y valida los
modelos, `grafico.py` compone la visualización y `generar.py` exporta
la aplicación, la serie, los miembros, las métricas y los errores.
`indicadores.json` contiene el periodo, la revisión de origen, la
regla del grupo y las metas y límites por indicador. Al incorporar
valores oficiales, actualiza las anualidades y marca `ilustrativos`
como `false`. Para incorporar otro indicador anual de escala no negativa,
añade una entrada con su código técnico, título, unidad, sentido
(`max` o `min`), metas y límites. Revisa la idoneidad del modelo,
la definición y la regla comparativa para cada indicador.

Para cambiar de revisión, contrasta ambas fuentes, actualiza la configuración,
regenera, vuelve a validar los agregados y actualiza la documentación.
Los CSV publicados quedan dentro del directorio de cada indicador.
`serie.csv` distingue observado, previsto y planificación. `grupo.csv`
incluye usuarios, préstamo y banderas de referencia. Los CSV usan
punto y coma, coma decimal y UTF-8 con BOM.

## Publicación

En Settings → Pages, selecciona GitHub Actions como origen. Un cambio en
`main` o la ejecución manual del workflow genera `site/`, ejecuta las
pruebas y despliega a GitHub Pages. El sitio incluye Plotly localmente
y funciona sin servidor Python. La revisión fija evita que un nuevo
despliegue incorpore cambios de la fuente sin revisión.
