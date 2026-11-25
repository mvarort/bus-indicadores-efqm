"""Composición estática y exportable de un indicador anual."""
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FuncFormatter, MaxNLocator
import pandas as pd

LIMITE = "#512060"
BUS = "#C8102E"
META = "#388E3C"
AZUL = "#C5DAEF"
BENCHMARK = "#487FB3"
REFERENCIA = "#254D76"
ALFA_BANDA = .53
ROSADO = "#F8D6DC"
TINTA = "#172637"
SECUNDARIO = "#45566A"
EXPORT_DPI = 200


CONTROLES = {
    "Histórico": {"bus_actual": "Resultado BUS", "target_historical": "Meta histórica",
                  "threshold_historical": "Límite histórico"},
    "Comparación externa": {"benchmark": "Benchmark", "reference": "Referencia del grupo",
                            "comparison_band": "Banda comparativa"},
    "Prospectiva": {"bus_forecast": "Previsión BUS", "target_future": "Meta futura",
                    "threshold_future": "Límite futuro"},
}

# Orden físico, anchura y color compartidos por el dibujo y la interfaz.
BARRAS = (
    (("threshold_historical", "limite", .18, LIMITE),
     ("bus_actual", "bus", .36, BUS),
     ("target_historical", "meta", .18, META)),
    (("threshold_future", "limite", .18, LIMITE),
     ("bus_forecast", "prevision", .36, BUS),
     ("target_future", "meta", .18, META)),
)
SEPARACION = .03


def numero(value):
    entero, _, decimales = f"{value:,.2f}".partition(".")
    fraccion = decimales.rstrip("0")
    return entero.replace(",", ".") + (f",{fraccion}" if fraccion else "")


def rotular_bus(ax, valores, serie, futuro):
    """Sitúa el valor en vertical dentro de cada barra observada o prevista."""
    color = "#85122A" if futuro else "white"
    fondo = dict(facecolor=ROSADO, edgecolor="none", boxstyle="round,pad=.20") if futuro else None
    for year, value in valores.items():
        etiqueta = ax.annotate(
            numero(value), (year, value), xytext=(0, -7), textcoords="offset points",
            ha="center", va="top", rotation=90, fontsize=9.5, fontweight="bold",
            color=color, bbox=fondo, zorder=7,
        )
        etiqueta.set_gid(f"serie-{serie}-etiqueta-{year}")


def grafico(panel, fin, titulo, subtitulo, unidad, modelo, ilustrativos):
    """Dibuja zonas comparativas, barras y notas utilizando los valores del CSV."""
    fig = Figure(figsize=(16, 7.4), facecolor="white")
    FigureCanvasAgg(fig)
    ax = fig.add_axes([.072, .228, .908, .511])
    hist = panel.loc[:fin]
    fut = panel.loc[fin + 1:]
    banda = ax.fill_between(hist.index, hist.benchmark, hist.referencia,
                           color=AZUL, alpha=ALFA_BANDA, linewidth=0, zorder=0)
    banda.set_gid("serie-comparison_band-historico")
    for serie, columna, color in [
        ("benchmark", "benchmark", BENCHMARK), ("reference", "referencia", REFERENCIA),
    ]:
        linea, = ax.plot(hist.index, hist[columna], color=color, linewidth=1.65, zorder=2)
        linea.set_gid(f"serie-{serie}-historico")

    for periodo, futuro, grupo in [(hist, False, BARRAS[0]), (fut, True, BARRAS[1])]:
        for (serie, columna, ancho, color), desplazamiento in zip(grupo, (-.30, 0, .30)):
            estilo = {"color": color}
            previsiones = serie == "bus_forecast"
            if futuro:
                estilo = {"facecolor": ROSADO if previsiones else "none",
                          "edgecolor": color, "linewidth": 1.1}
                if previsiones:
                    estilo["hatch"] = "///"
            valores = periodo[columna]
            barras = ax.bar(valores.index + desplazamiento, valores, width=ancho, zorder=3, **estilo)
            for year, barra in zip(valores.index, barras):
                barra.set_gid(f"serie-{serie}-barra-{year}")
            if serie in {"bus_actual", "bus_forecast"}:
                rotular_bus(ax, valores, serie, futuro)

    superior = panel[["bus", "referencia", "prevision", "limite", "meta"]].max().max()
    ax.set_ylim(0, superior * 1.13)
    ax.set_xlim(panel.index[0] - .52, panel.index[-1] + .52)
    ax.set_xticks(panel.index, [str(y) for y in panel.index], fontsize=9, fontweight="medium")
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6, steps=[1, 2, 2.5, 5, 10]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: numero(value)))
    ax.tick_params(axis="both", length=0, pad=8, colors=SECUNDARIO, labelsize=9)
    ax.grid(axis="y", color="#DFE5EC", linewidth=.65, zorder=1)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#AEBAC8")
    ax.axvline(fin + .5, color="#AEBAC8", linewidth=.8, linestyle=(0, (2, 4)), zorder=2)
    ax.text(panel.index[0] - .52, 1.07, unidad, transform=ax.get_xaxis_transform(),
            size=9, color=SECUNDARIO, ha="left", va="bottom")
    for centro, nombre in [((hist.index[0] + hist.index[-1]) / 2, "Histórico"),
                            ((fut.index[0] + fut.index[-1]) / 2, "Prospectiva")]:
        ax.text(centro, 1.025, nombre, transform=ax.get_xaxis_transform(),
                size=10, weight="semibold", color=SECUNDARIO, ha="center")

    fig.text(.047, .941, titulo, fontsize=23, weight="bold", color=TINTA, va="top")
    fig.text(.048, .878, subtitulo, fontsize=11, color=SECUNDARIO, va="top")

    elementos = [
        ("threshold", Patch(facecolor=LIMITE, label="Límite")),
        ("bus_actual", Patch(facecolor=BUS, label="BUS")),
        ("target", Patch(facecolor=META, label="Meta")),
        ("bus_forecast", Patch(facecolor=ROSADO, edgecolor=BUS, hatch="///", label="Previsión BUS")),
        ("benchmark", Line2D([], [], color=BENCHMARK, linewidth=1.65, label="Benchmark")),
        ("reference", Line2D([], [], color=REFERENCIA, linewidth=1.65, label="Referencia del grupo")),
        ("comparison_band", Patch(facecolor=AZUL, alpha=ALFA_BANDA, label="Banda comparativa")),
    ]
    leyenda = fig.legend(handles=[handle for _, handle in elementos],
                         loc="upper left", bbox_to_anchor=(.047, .842),
                         borderaxespad=0, ncols=len(elementos), frameon=False, fontsize=9.5,
                         columnspacing=1.65, handlelength=1.6, labelcolor=TINTA)
    for (serie, _), muestra, etiqueta in zip(elementos, leyenda.legend_handles, leyenda.get_texts()):
        muestra.set_gid(f"leyenda-{serie}-muestra")
        etiqueta.set_gid(f"leyenda-{serie}-texto")

    fig.add_artist(Line2D([.047, .98], [.155, .155], transform=fig.transFigure,
                          color="#DFE5EC", linewidth=.7))
    notas = [
        ("fuente", "Fuente  REBIUN Data Explorer."),
        ("comparacion", "Benchmark = mediana del grupo comparador · Referencia del grupo = mejor resultado anual."),
        ("plan", "Metas y límites ilustrativos." if ilustrativos else "Metas y límites oficiales."),
        ("prevision", f"Previsión mediante {modelo.lower()}. Estimaciones sujetas a incertidumbre, sin intervalo calibrado."),
    ]
    for i, (clave, nota) in enumerate(notas):
        artista = fig.text(.048, .130 - i * .026, nota, fontsize=9, color=SECUNDARIO, va="top")
        artista.set_gid(f"nota-{clave}")
    return fig


def exportar(fig, destino):
    """Exporta la misma composición al PNG principal y al SVG vectorial."""
    fig.savefig(destino / "grafica.png", dpi=EXPORT_DPI)
    fig.savefig(destino / "grafica.svg", format="svg",
                metadata={"Title": fig.texts[0].get_text(), "Date": None})
