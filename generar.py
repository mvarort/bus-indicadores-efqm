"""Genera la aplicación estática y las tablas reproducibles de cada indicador."""
import argparse
import json
from html import escape
from pathlib import Path

import pandas as pd
import plotly.io as pio
from plotly.offline import get_plotlyjs

from datos import ID, cargar, preparar
from grafico import grafico, numero
from prevision import evaluar


def tabla(headers, rows):
    head = "".join(f'<th scope="col">{escape(str(x))}</th>' for x in headers)
    body = "".join("<tr>" + "".join(
        f"<td>{escape(str(x))}</td>" for x in row
    ) + "</tr>" for row in rows)
    return f'<div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


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
        panel[col] = pd.Series({int(y): v for y, v in ajuste[key].items()}, dtype=float)
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
    fig = grafico(panel, fin, ajuste["unidad"], ajuste["ilustrativos"])
    chart = pio.to_html(
        fig, full_html=False, include_plotlyjs=False, div_id="grafico",
        config={"displaylogo": False, "displayModeBar": False, "responsive": True,
                "scrollZoom": False},
    )
    anuales = tabla(
        ["Año", "Resultado BUS", "Previsión BUS", "Límite", "Meta", "Mediana", "Referencia", "Grupo con dato / total"],
        [[y, *[numero(row[k]) for k in ["bus","prevision","limite","meta","benchmark","referencia"]],
          f"{numero(row.con_dato)} / {numero(row.elegibles)}" if y <= fin else "—"]
         for y, row in panel.iterrows()],
    )
    grupos = []
    for year, grupo in miembros.groupby("Anio"):
        lideres = ", ".join(grupo.loc[grupo.referencia, "Biblioteca"]) or "Sin dato"
        contenido = tabla(
            ["Código", "Biblioteca", "Usuarios propios", ajuste["unidad"], "Referencia"],
            [(r[ID], r.Biblioteca, numero(r.NUSUARIOPROP), numero(r[codigo]), "Sí" if r.referencia else "")
             for _, r in grupo.iterrows()],
        )
        grupos.append(f"<details><summary>{year} · {len(grupo)} bibliotecas · {escape(lideres)}</summary>{contenido}</details>")
    validacion = tabla(
        ["Modelo", "Horizonte", "Orígenes", "MAE", "RMSE"],
        [(r.modelo, r.horizonte, r.n, numero(round(r.mae)), numero(round(r.rmse))) for r in metricas.itertuples()],
    )
    controles = "".join(
        f'<label><input type="checkbox" data-serie="{i}" checked> {escape(trace.name)}</label>'
        for i, trace in enumerate(fig.data)
    )
    origen = f"{config['fuente']}/tree/{config['revision']}/data"
    aviso = "Metas y límites ilustrativos." if ajuste["ilustrativos"] else "Metas y límites oficiales."
    plantilla = Path(__file__).with_name("pagina.html").read_text(encoding="utf-8")
    from string import Template
    html = Template(plantilla).substitute(
        titulo=escape(ajuste["titulo"]), codigo=escape(codigo), fin=fin, inicio=config["inicio"],
        ultimo=years.stop - 1, valor=numero(hist.bus.iloc[-1]), mediana=numero(hist.benchmark.iloc[-1]),
        futuro=numero(panel.prevision.loc[fin + 1]), primer_futuro=fin + 1,
        modelo=escape(modelo), aviso=aviso, umbral=numero(config["umbral_usuarios"]),
        chart=chart, anuales=anuales, grupos="".join(grupos), validacion=validacion,
        controles=controles, fuente=escape(origen),
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
    (args.salida / "plotly.min.js").write_text(get_plotlyjs(), encoding="utf-8")
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
