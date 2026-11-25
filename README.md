# Indicadores EFQM 2028

Prototipo de una lámina por indicador, preparada para incorporarse como imagen en la plataforma de evaluación EFQM. La página pública permite probar combinaciones de nueve elementos en tres bloques. Los elementos visibles se reagrupan por año y determinan la leyenda, las notas y el PNG descargado. Cada serie tiene una casilla de cifras independiente. Las etiquetas aparecen cuando su serie es visible. Las cifras comparativas se alinean bajo cada año y la etiqueta de la banda muestra los dos extremos. «Restablecer selección» vuelve a mostrar todos los elementos y solo las cifras BUS. Los enlaces directos a PNG y SVG ofrecen la lámina con la selección inicial completa.

[Ver la lámina](https://mvarort.github.io/bus-indicadores-efqm/NPRESTDOMIC/) ·
[Descargar PNG de 3.200 × 1.480 px](https://mvarort.github.io/bus-indicadores-efqm/NPRESTDOMIC/grafica.png) ·
[SVG vectorial](https://mvarort.github.io/bus-indicadores-efqm/NPRESTDOMIC/grafica.svg) ·
[Serie CSV](https://mvarort.github.io/bus-indicadores-efqm/NPRESTDOMIC/serie.csv) ·
[Metodología y limitaciones](metodologia.md).

## Indicadores

- [Préstamos domiciliarios de material bibliográfico](https://mvarort.github.io/bus-indicadores-efqm/NPRESTDOMIC/).
- [Monografías electrónicas de pago](https://mvarort.github.io/bus-indicadores-efqm/NMONPAGOLIC/).
- [Personas usuarias por puesto de lectura](https://mvarort.github.io/bus-indicadores-efqm/USUARIOS_POR_PUESTO/).
- [Porcentaje del gasto en información electrónica](https://mvarort.github.io/bus-indicadores-efqm/PCT_GASTO_ELECTRONICO/).

Usa el desplegable para cambiar la lámina. La siguiente página recibe
la selección de series y cifras, y «Descargar imagen PNG» recoge el
indicador y los elementos visibles en ese momento. Cada carpeta pública
incluye `grafica.png`, `grafica.svg`, `serie.csv` y los CSV de grupo y
validación.

## Instalación y generación

Con Python 3.11:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python generar.py
python -m unittest -v
python -m http.server 8000 --directory site
```

Abre http://localhost:8000. El generador obtiene los CSV públicos de la revisión fijada en `indicadores.json`. Para trabajar sin red, ejecuta `python generar.py --datos /ruta/a/data` y `REBIUN_DATOS=/ruta/a/data python -m unittest -v`. Usa la misma carpeta con ambos CSV originales.

## Actualización

- `datos.py` lee y cruza las fuentes.
- `prevision.py` ajusta y valida los modelos.
- `grafico.py` compone una figura estática con Matplotlib y exporta PNG y SVG.
- `generar.py` escribe la página de cada indicador, ambas imágenes y sus CSV.
- `selector.js` actualiza la figura SVG incrustada y rasteriza esa misma versión a PNG de 3.200 × 1.480 px.
- `indicadores.json` contiene periodo, revisión de origen, regla del grupo y metas y límites por indicador y año. Los valores incluidos para 2016–2028 son ilustrativos. Cuando existan valores oficiales, sustituye las dos series completas y actualiza `ilustrativos`.

El generador reutiliza esta composición para indicadores anuales de escala no negativa. Añade una clave de indicador con variable REBIUN o fórmula de razón, título, subtítulo, unidad, precisión, polaridad, límites naturales, configuración predictiva, notas y metas y límites por año. Usa `mejor: max` para polaridad creciente y `mejor: min` para decreciente. Si la polaridad está pendiente, documenta explícitamente una referencia descriptiva. Revisa la idoneidad estadística y comparativa para cada incorporación. Los contrastes automatizados cubren las cuatro series de la revisión publicada.

Los originales se consultan desde una revisión fija. Al cambiarla, contrasta las definiciones y las campañas, regenera, valida la serie y actualiza la documentación y `datos_procesados/`. Los CSV usan punto y coma, coma decimal y UTF-8 con BOM. La [instantánea procesada](datos_procesados/) conserva la serie anual, los miembros del grupo, la validación por horizonte y los errores por origen.

## Publicación

En Settings → Pages, se selecciona GitHub Actions como origen. Un cambio en `main` o la ejecución manual del workflow genera `site/`, ejecuta las pruebas y despliega. La imagen puede utilizarse de forma independiente de la página.
