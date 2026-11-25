"""Genera la aplicación estática y las tablas reproducibles de cada indicador."""
import argparse
import json
from html import escape
from pathlib import Path
from string import Template

import numpy as np
import pandas as pd

from datos import cargar, preparar
from grafico import exportar, grafico
from prevision import evaluar


def csv(df, salida, nombre, index=False):
    df.to_csv(salida / nombre, index=index, encoding="utf-8-sig", sep=";", decimal=",")


def pagina(config, codigo, datos, centros, root):
    ajuste = config["indicadores"][codigo]
    fin = config["fin"]
    hist, miembros = preparar(datos, centros, config, codigo)
    modelo, pred, metricas, errores, ranking = evaluar(hist.bus, config["horizonte"])
    years = range(fin + 1, fin + 1 + len(pred))
    panel = hist.reindex(range(config["inicio"], years.stop))
    panel["prevision"] = pd.Series(pred.round(), index=years)
    for col, key in [("limite", "limites"), ("meta", "metas")]:
        valores = pd.Series({int(y): v for y, v in ajuste[key].items()}, dtype=float)
        panel[col] = valores.reindex(panel.index)
        if not np.isfinite(panel[col]).all() or (panel[col] < 0).any():
            raise ValueError(f"{codigo}: se requieren {key} no negativos para todas las anualidades")
    panel["naturaleza_bus"] = ["Observado" if y <= fin else "Previsto" for y in panel.index]
    panel["naturaleza_plan"] = [
        ("Ilustrativo" if ajuste["ilustrativos"] else "Oficial")
        if pd.notna(row.meta) or pd.notna(row.limite) else ""
        for row in panel.itertuples()
    ]
    destino = root / codigo
    destino.mkdir(parents=True, exist_ok=True)
    csv(panel, destino, "serie.csv", index=True)
    csv(miembros, destino, "grupo.csv")
    csv(metricas, destino, "validacion.csv")
    csv(errores, destino, "errores-validacion.csv")
    csv(ranking.rename_axis("modelo"), destino, "seleccion.csv", index=True)
    fig = grafico(panel, fin, ajuste["titulo"], ajuste["subtitulo"], ajuste["unidad"],
                  modelo, ajuste["ilustrativos"])
    exportar(fig, destino)
    plantilla = Path(__file__).with_name("pagina.html").read_text(encoding="utf-8")
    html = Template(plantilla).substitute(
        titulo=escape(ajuste["titulo"]), subtitulo=escape(ajuste["subtitulo"]),
        inicio=config["inicio"], fin=fin, primer_futuro=fin + 1, ultimo=years.stop - 1,
    )
    (destino / "index.html").write_text(html, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, help="Carpeta local con los dos CSV originales")
    parser.add_argument("--salida", type=Path, default=Path("site"))
    args = parser.parse_args()
    config = json.loads(Path(__file__).with_name("indicadores.json").read_text(encoding="utf-8"))
    args.salida.mkdir(parents=True, exist_ok=True)
    datos, centros = cargar(config, args.datos)
    (args.salida / "metodologia.md").write_text(
        Path(__file__).with_name("metodologia.md").read_text(encoding="utf-8").replace("](datos_procesados/", "](NPRESTDOMIC/"),
        encoding="utf-8"
    )
    enlaces = []
    for codigo, ajuste in config["indicadores"].items():
        pagina(config, codigo, datos, centros, args.salida)
        enlaces.append(f'<li><a href="{escape(codigo)}/">{escape(ajuste["titulo"])}</a></li>')
    redirect = ""
    if len(enlaces) == 1:
        redirect = f'<meta http-equiv="refresh" content="0;url={escape(next(iter(config["indicadores"])))}/">'
    (args.salida / "index.html").write_text(
        f'<!doctype html><html lang="es"><meta charset="utf-8">{redirect}<title>Indicadores BUS</title>'
        f'<h1>Indicadores BUS</h1><ul>{"".join(enlaces)}</ul></html>', encoding="utf-8"
    )


if __name__ == "__main__":
    main()
