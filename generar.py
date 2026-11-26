"""Genera la aplicación estática y las tablas reproducibles de cada indicador."""
import argparse
import json
from hashlib import sha256
from itertools import combinations_with_replacement
from html import escape
from pathlib import Path
from string import Template

import numpy as np
import pandas as pd

from datos import cargar, preparar
from etiquetas import geometria_etiquetas, situar_estaticas
from grafico import BARRAS, CONTROLES, ETIQUETAS_INICIALES, SEPARACION, exportar, grafico, svg_figura
from prevision import evaluar
from intervalos import METODOS, evaluar_intervalos
from revision_predictiva import MINIMOS_RECIENTE, estudiar, pronosticar


def csv(df, salida, nombre, index=False):
    df.to_csv(salida / nombre, index=index, encoding="utf-8-sig", sep=";", decimal=",")


def pagina(config, codigo, datos, centros, root, version_selector):
    ajuste = config["indicadores"][codigo]
    fin = config["fin"]
    hist, miembros = preparar(datos, centros, config, codigo)
    minimo, maximo = ajuste["limites_naturales"]
    prevision = ajuste["prevision"]
    if prevision["metodo"] != "validacion_temporal":
        raise ValueError(f"{codigo}: método de previsión no admitido")
    horizonte_maximo = max(config["horizontes"])
    _, _, metricas, errores, ranking = evaluar(
        hist.bus, horizonte_maximo, limites=(minimo, maximo), horizonte_seleccion=config["horizonte"],
        entrenamiento_minimo=prevision["entrenamiento_minimo"], escala_ajuste=prevision["escala_ajuste"],
    )
    limites = (minimo, maximo)
    escala = prevision["escala_ajuste"]
    catalogo, detalle_revision, metricas_revision, escenarios = estudiar(
        hist.bus, horizonte_maximo, limites, prevision,
    )
    modelo = prevision["modelo_publicado"]
    transformacion = prevision["transformacion"]
    ventana = hist.bus.loc[prevision["inicio_ajuste"]:]
    periodo_ajuste = f"{ventana.index[0]}–{ventana.index[-1]} (n={len(ventana)})"
    modelo_grafico = f"{modelo} en escala logit" if transformacion == "logit" else modelo
    pred = pronosticar(ventana, modelo, horizonte_maximo, limites, escala, transformacion)
    minimo_cobertura = (MINIMOS_RECIENTE[modelo] if ventana.index[0] > hist.index[0]
                        else prevision["entrenamiento_minimo"])
    extremos, detalle_intervalos, cobertura = evaluar_intervalos(
        ventana, modelo, horizonte_maximo, limites, minimo_cobertura, escala, transformacion,
    )
    years = range(fin + 1, fin + 1 + len(pred))
    panel = hist.reindex(range(config["inicio"], years.stop))
    panel["prevision"] = pd.Series(pred.round(ajuste["decimales"]), index=years)
    for i, campo in enumerate(("prediccion_inferior_95", "prediccion_superior_95")):
        panel[campo] = pd.Series(extremos[:, i], index=years)
    for col, key in [("limite", "limites"), ("meta", "metas")]:
        valores = pd.Series({int(y): v for y, v in ajuste[key].items()}, dtype=float)
        panel[col] = valores.reindex(panel.index)
        if (not np.isfinite(panel[col]).all() or panel[col].lt(minimo).any()
                or (maximo is not None and panel[col].gt(maximo).any())):
            raise ValueError(f"{codigo}: se requieren {key} dentro de los límites naturales cada año")
    if ajuste["polaridad"] == "decreciente" and not panel.meta.lt(panel.limite).all():
        raise ValueError(f"{codigo}: la meta debe ser menor que el límite en cada año")
    panel["naturaleza_bus"] = ["Observado" if y <= fin else "Previsto" for y in panel.index]
    panel["naturaleza_plan"] = [
        ("Ilustrativo" if ajuste["ilustrativos"] else "Oficial")
        if pd.notna(row.meta) or pd.notna(row.limite) else ""
        for row in panel.itertuples()
    ]
    destino = root / codigo
    destino.mkdir(parents=True, exist_ok=True)
    csv(miembros, destino, "grupo.csv")
    csv(metricas, destino, "validacion.csv")
    csv(errores, destino, "errores-validacion.csv")
    csv(ranking.rename_axis("modelo"), destino, "seleccion.csv", index=True)
    csv(detalle_intervalos, destino, "validacion-intervalos.csv")
    csv(cobertura, destino, "cobertura-intervalos.csv", index=True)
    csv(catalogo, destino, "revision-candidatos.csv")
    csv(detalle_revision, destino, "revision-errores.csv")
    csv(metricas_revision, destino, "revision-metricas.csv")
    csv(escenarios, destino, "revision-escenarios.csv")
    csv(pd.DataFrame([{"modelo": modelo, "transformacion": transformacion,
                      "inicio": ventana.index[0], "fin": ventana.index[-1], "n_ajuste": len(ventana)}]),
        destino, "ajuste-publicado.csv")
    cambios = pd.DataFrame({"observado": hist.bus, "cambio_anual": hist.bus.diff(),
                            "cambio_relativo": hist.bus.pct_change()})
    csv(cambios, destino, "diagnostico-serie.csv", index=True)
    nota_intervalo = METODOS[modelo] if np.isfinite(extremos).any() else ""
    for horizonte in config["horizontes"]:
        sufijo = "" if horizonte == config["horizonte"] else f"-{horizonte}"
        vista = panel.loc[:fin + horizonte]
        csv(vista, destino, f"serie{sufijo}.csv", index=True)
        dibujar_pagina(config, codigo, ajuste, vista, modelo_grafico, destino, horizonte, sufijo,
                       nota_intervalo, version_selector, periodo_ajuste)
    for inicial, final in combinations_with_replacement(range(config["inicio"], fin + 1), 2):
        if (inicial, final) == (config["inicio"], fin):
            continue
        horizontes = config["horizontes"] if final == fin else [0]
        for horizonte in horizontes:
            vista = panel.loc[inicial:final + horizonte]
            dibujar_pagina(config, codigo, ajuste, vista, modelo_grafico, destino, horizonte, "",
                           nota_intervalo if horizonte else None, version_selector, periodo_ajuste,
                           final_visible=final)


def opciones_anuales(inicio, fin, seleccionado, menor, mayor):
    opciones = []
    for year in range(inicio, fin + 1):
        estado = " selected" if year == seleccionado else ""
        if not menor <= year <= mayor:
            estado += " disabled"
        opciones.append(f'<option value="{year}"{estado}>{year}</option>')
    return "".join(opciones)


def dibujar_pagina(config, codigo, ajuste, panel, modelo, destino, horizonte, sufijo,
                  nota_intervalo, version_selector, periodo_ajuste, final_visible=None):
    fin = config["fin"]
    inicial = int(panel.index[0])
    final = fin if final_visible is None else final_visible
    periodo_visible = f"{inicial}–{final}" if inicial != final else str(inicial)
    subtitulo = ajuste.get("subtitulo", config["subtitulo"])
    fig = grafico(panel, final, ajuste["titulo"], f"{subtitulo} · Histórico: {periodo_visible}",
                  ajuste["unidad"], modelo, ajuste["ilustrativos"], decimales=ajuste["decimales"],
                  maximo=ajuste["limites_naturales"][1], notas_indicador=ajuste["notas"],
                  polaridad=ajuste["polaridad"], unidad_porcentual=ajuste.get("formato") == "porcentaje",
                  nota_intervalo=nota_intervalo, periodo_ajuste=periodo_ajuste, periodo_visible=periodo_visible)
    disposicion = geometria_etiquetas(fig)
    if final_visible is None:
        situar_estaticas(fig, disposicion)
        exportar(fig, destino, sufijo)
        svg = (destino / f"grafica{sufijo}.svg").read_text(encoding="utf-8")
        archivo = f"{horizonte}.html" if sufijo else "index.html"
    else:
        svg = svg_figura(fig)
        variante = f"-{horizonte}" if horizonte and horizonte != config["horizonte"] else ""
        archivo = f"historico-{inicial}-{final}{variante}.html"
    plantilla = Path(__file__).with_name("pagina.html").read_text(encoding="utf-8")
    controles = []
    for titulo, opciones in CONTROLES.items():
        casillas = []
        for serie, nombre in opciones.items():
            marcada = " checked" if serie in ETIQUETAS_INICIALES else ""
            if serie == "comparison_band":
                cifra = f'<input type="checkbox" data-etiqueta="{serie}" disabled hidden><span aria-hidden="true">—</span>'
            else:
                cifra = f'<input type="checkbox" data-etiqueta="{serie}" aria-label="Cifras de {nombre}"{marcada}>'
            casillas.append(
                f'<label><input type="checkbox" name="{serie}" checked> {nombre}</label>'
                + cifra
            )
        controles.append(
            f'<fieldset{" hidden" if titulo == "Prospectiva" and not horizonte else ""}><legend>{titulo}</legend><div class="series">'
            f'<span>Serie</span><span>Cifras</span>{"".join(casillas)}</div></fieldset>'
        )
    svg = svg[svg.index("<svg "):]
    escala = fig.axes[0].get_position().width * fig.get_figwidth() * 72 / np.ptp(fig.axes[0].get_xlim())
    geometria = {
        **disposicion, "escala": escala, "separacion": SEPARACION,
        "grupos": [[{"id": serie, "ancho": ancho, "origen": origen, "color": color}
                    for (serie, _, ancho, color), origen in zip(grupo, (-.30, 0, .30))]
                   for grupo in BARRAS],
    }
    opciones = []
    for otro_id, otro in config["indicadores"].items():
        seleccionado = " selected" if otro_id == codigo else ""
        opciones.append(f'<option value="../{escape(otro_id)}/"{seleccionado}>{escape(otro["titulo"])}</option>')
    horizontes = []
    for opcion in config["horizontes"]:
        seleccionado = " selected" if opcion == horizonte else ""
        horizontes.append(f'<option value="{opcion}"{seleccionado}>{opcion} años · {fin + 1}–{fin + opcion}</option>')
    html = Template(plantilla).substitute(
        titulo=escape(ajuste["titulo"]), indicadores="".join(opciones), controles="".join(controles), grafica=svg,
        geometria=json.dumps(geometria), version_selector=version_selector,
        horizontes="".join(horizontes), horizonte=horizonte, codigo=escape(codigo),
        inicio_disponible=config["inicio"], fin_disponible=fin,
        horizonte_inicial=config["horizonte"], prospectiva_oculta="" if horizonte else " hidden",
        anios_iniciales=opciones_anuales(config["inicio"], fin, inicial, config["inicio"], final),
        anios_finales=opciones_anuales(config["inicio"], fin, final, inicial, fin),
        intervalo_control="" if nota_intervalo else " disabled",
    )
    (destino / archivo).write_text(html, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--datos", type=Path, help="Carpeta local con los dos CSV originales")
    parser.add_argument("--salida", type=Path, default=Path("site"))
    args = parser.parse_args()
    config = json.loads(Path(__file__).with_name("indicadores.json").read_text(encoding="utf-8"))
    args.salida.mkdir(parents=True, exist_ok=True)
    datos, centros = cargar(config, args.datos)
    script = Path(__file__).with_name("selector.js").read_bytes()
    (args.salida / "selector.js").write_bytes(script)
    colocacion = Path(__file__).with_name("colocacion.js").read_bytes()
    (args.salida / "colocacion.js").write_bytes(colocacion)
    version_selector = sha256(script + colocacion).hexdigest()[:12]
    (args.salida / "metodologia.md").write_text(
        Path(__file__).with_name("metodologia.md").read_text(encoding="utf-8").replace("](datos_procesados/", "](NPRESTDOMIC/"),
        encoding="utf-8"
    )
    enlaces = []
    for codigo, ajuste in config["indicadores"].items():
        pagina(config, codigo, datos, centros, args.salida, version_selector)
        enlaces.append(f'<li><a href="{escape(codigo)}/">{escape(ajuste["titulo"])}</a></li>')
    redirect = ""
    if enlaces:
        redirect = f'<meta http-equiv="refresh" content="0;url={escape(next(iter(config["indicadores"])))}/">'
    (args.salida / "index.html").write_text(
        f'<!doctype html><html lang="es"><meta charset="utf-8">{redirect}<title>Indicadores BUS</title>'
        f'<h1>Indicadores BUS</h1><ul>{"".join(enlaces)}</ul></html>', encoding="utf-8"
    )


if __name__ == "__main__":
    main()
