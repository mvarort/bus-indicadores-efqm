# Indicadores EFQM 2028

Prototipo de una lámina por indicador, preparada para incorporarse como imagen en la plataforma de evaluación EFQM. La página pública muestra la misma lámina que el PNG.

[Ver la lámina](https://mvarort.github.io/bus-indicadores-efqm/NPRESTDOMIC/) ·
[Descargar PNG de 3.200 × 1.480 px](https://mvarort.github.io/bus-indicadores-efqm/NPRESTDOMIC/grafica.png) ·
[SVG vectorial](https://mvarort.github.io/bus-indicadores-efqm/NPRESTDOMIC/grafica.svg) ·
[Serie CSV](https://mvarort.github.io/bus-indicadores-efqm/NPRESTDOMIC/serie.csv) ·
[Metodología y limitaciones](metodologia.md).

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
- `indicadores.json` contiene periodo, revisión de origen, regla del grupo y metas y límites por indicador y año. Los valores incluidos para 2016–2028 son ilustrativos. Cuando existan valores oficiales, sustituye las dos series completas y actualiza `ilustrativos`.

El generador reutiliza esta composición para indicadores anuales de escala no negativa. Añade el código técnico, el título, el subtítulo, la unidad, el sentido y las metas y límites por año. Revisa la idoneidad estadística y comparativa para cada indicador. El contraste automatizado de referencia está fijado a NPRESTDOMIC y la revisión publicada.

Los originales se consultan desde una revisión fija. Al cambiarla, contrasta las definiciones y las campañas, regenera, valida la serie y actualiza la documentación y `datos_procesados/`. Los CSV usan punto y coma, coma decimal y UTF-8 con BOM. La [instantánea procesada](datos_procesados/) conserva la serie anual, los miembros del grupo, la validación por horizonte y los errores por origen.

## Publicación

En Settings → Pages, se selecciona GitHub Actions como origen. Un cambio en `main` o la ejecución manual del workflow genera `site/`, ejecuta las pruebas y despliega. La imagen puede utilizarse de forma independiente de la página.
