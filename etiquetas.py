"""Adaptador de Matplotlib para el algoritmo compartido de colocación."""
import json
from pathlib import Path
import subprocess

import numpy as np


def geometria_etiquetas(fig):
    """Proyecta líneas y marcadores a las coordenadas del SVG."""
    ax = fig.axes[0]
    escala = 72 / fig.dpi
    alto = fig.get_figheight() * 72

    def transformar(x, y):
        px, py = ax.transData.transform((x, y)) * escala
        return float(px), float(alto - py)

    segmentos = {}
    for linea in ax.lines:
        id_linea = linea.get_gid() or ""
        if not id_linea.startswith("serie-"):
            continue
        serie = id_linea.split("-")[1]
        puntos = [transformar(x, y) if np.isfinite(x) and np.isfinite(y) else None
                  for x, y in zip(linea.get_xdata(), linea.get_ydata())]
        trazos = segmentos.setdefault(serie, [])
        if linea.get_linestyle() not in {"None", "none", " ", ""}:
            trazos.extend([*a, *b, linea.get_linewidth()/2]
                          for a, b in zip(puntos, puntos[1:]) if a is not None and b is not None)
        if linea.get_marker() not in {"None", "none", " ", ""}:
            trazos.extend([*p, *p, (linea.get_markersize()+linea.get_markeredgewidth())/2]
                          for p in puntos if p is not None)

    x, y = transformar(ax.get_xlim()[0], ax.get_ylim()[1])
    derecha, base = transformar(ax.get_xlim()[1], 0)
    return {"segmentos": segmentos, "limites": {"x": x, "y": y, "w": derecha-x, "h": base-y}}


def situar_estaticas(fig, geometrias):
    """Mide los glifos rasterizados para las imágenes iniciales del repositorio."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    ax = fig.axes[0]
    escala = 72 / fig.dpi
    alto = fig.get_figheight()*72

    def caja(artista):
        limites = artista.get_window_extent(renderer)
        return dict(x=limites.x0*escala, y=alto-limites.y1*escala,
                    w=limites.width*escala, h=limites.height*escala)

    barras = {barra.get_gid(): barra for grupo in ax.containers for barra in grupo.patches}
    etiquetas = [a for a in ax.texts if a.get_visible() and (a.get_gid() or "").startswith("etiqueta-")]
    entradas = []
    for etiqueta in etiquetas:
        _, serie, year = etiqueta.get_gid().split("-")
        entradas.append({"texto": caja(etiqueta), "barra": caja(barras[f"serie-{serie}-barra-{year}"])})
    carga = dict(etiquetas=entradas, limites=geometrias["limites"],
                 segmentos=[t for grupo in geometrias["segmentos"].values() for t in grupo],
                 margen=1.8, barras=[caja(a) for a in barras.values()])
    comando = ["node", str(Path(__file__).with_name("colocacion.js"))]
    resultado = subprocess.run(comando, input=json.dumps(carga), text=True, capture_output=True, check=True)
    for etiqueta, entrada, destino in zip(etiquetas, entradas, json.loads(resultado.stdout)):
        if destino is None:
            continue
        x, y = etiqueta.get_position()
        texto = entrada["texto"]
        etiqueta.set_position((x + destino["x"]-texto["x"], y + texto["y"]-destino["y"]))
        if destino["exterior"]:
            etiqueta.set_color("#9B1025")
        if destino["exterior"] or etiqueta.get_gid().startswith("etiqueta-bus_forecast-"):
            fondo = "#FFFFFF" if destino["exterior"] else "#FBE7EA"
            etiqueta.set_bbox(dict(facecolor=fondo, edgecolor="none", boxstyle="square,pad=.12"))
