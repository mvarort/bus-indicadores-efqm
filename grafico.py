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
AZUL = "#D6E7F5"
AMARILLO = "#F5E8C5"
ROSADO = "#F8D6DC"
TINTA = "#172637"
SECUNDARIO = "#45566A"
EXPORT_DPI = 200


def numero(value):
    entero, _, decimales = f"{value:,.2f}".partition(".")
    fraccion = decimales.rstrip("0")
    return entero.replace(",", ".") + (f",{fraccion}" if fraccion else "")


def barras(ax, valores, desplazamiento, ancho, nombre, **estilo):
    return ax.bar(valores.index + desplazamiento, valores, width=ancho, label=nombre, **estilo)


def rotular_bus(ax, valores, futuro=False):
    """Sitúa el valor en vertical dentro de cada barra observada o prevista."""
    color = "#85122A" if futuro else "white"
    fondo = dict(facecolor=ROSADO, edgecolor="none", boxstyle="round,pad=.20") if futuro else None
    for year, value in valores.items():
        ax.annotate(
            numero(value), (year, value), xytext=(0, -7), textcoords="offset points",
            ha="center", va="top", rotation=90, fontsize=9.5, fontweight="bold",
            color=color, bbox=fondo, zorder=7,
        )


def grafico(panel, fin, titulo, subtitulo, unidad, modelo, ilustrativos):
    """Dibuja zonas comparativas, barras y notas utilizando los valores del CSV."""
    fig = Figure(figsize=(16, 7.4), facecolor="white")
    FigureCanvasAgg(fig)
    ax = fig.add_axes([.072, .228, .908, .511])
    hist = panel.loc[:fin]
    fut = panel.loc[fin + 1:]
    comparables = hist.dropna(subset=["benchmark", "referencia"])
    ax.bar(comparables.index, comparables.benchmark, width=.94,
           color=AZUL, label="Benchmark", zorder=0)
    ax.bar(comparables.index, comparables.referencia - comparables.benchmark,
           bottom=comparables.benchmark, width=.94, color=AMARILLO,
           label="Referencia del grupo", zorder=0)

    for periodo, futuro in [(hist, False), (fut, True)]:
        for col, desplazamiento, ancho, color, nombre in [
            ("limite", -.30, .18, LIMITE, "Límite"),
            ("prevision" if futuro else "bus", 0, .36, BUS, "BUS previsto" if futuro else "BUS observado"),
            ("meta", .30, .18, META, "Meta"),
        ]:
            estilo = {"color": color}
            if futuro:
                estilo = {"facecolor": ROSADO if col == "prevision" else "none",
                          "edgecolor": color, "linewidth": 1.1}
                if col == "prevision":
                    estilo["hatch"] = "///"
            barras(ax, periodo[col], desplazamiento, ancho, nombre, zorder=3, **estilo)

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

    rotular_bus(ax, hist.bus)
    rotular_bus(ax, fut.prevision, futuro=True)

    fig.text(.047, .941, titulo, fontsize=23, weight="bold", color=TINTA, va="top")
    fig.text(.048, .878, subtitulo, fontsize=11, color=SECUNDARIO, va="top")

    leyenda = [
        Patch(facecolor=LIMITE, label="Límite"),
        Patch(facecolor=BUS, label="BUS observado"),
        Patch(facecolor=META, label="Meta"),
        Patch(facecolor=ROSADO, edgecolor=BUS, hatch="///", label="BUS previsto"),
        Patch(facecolor=AZUL, label="Benchmark"),
        Patch(facecolor=AMARILLO, label="Referencia del grupo"),
    ]
    fig.legend(handles=leyenda, loc="upper left", bbox_to_anchor=(.047, .842),
               borderaxespad=0, ncols=6, frameon=False, fontsize=9.5,
               columnspacing=1.65, handlelength=1.6, labelcolor=TINTA)
    fig.add_artist(Line2D([.047, .98], [.155, .155], transform=fig.transFigure,
                                    color="#DFE5EC", linewidth=.7))
    fig.text(.048, .125, "Fuente  REBIUN Data Explorer · Benchmark = mediana del grupo comparador · "
             "Referencia del grupo = mejor resultado anual.",
             fontsize=9, color=SECUNDARIO, va="top")
    plan = "Metas y límites ilustrativos" if ilustrativos else "Metas y límites oficiales"
    fig.text(.048, .087, f"{plan} (en contorno para la prospectiva).  Previsión mediante {modelo.lower()}. "
             "Estimaciones sujetas a incertidumbre, sin intervalo de predicción calibrado.",
             fontsize=9, color=SECUNDARIO, va="top")
    return fig


def exportar(fig, destino):
    """Exporta la misma composición al PNG principal y al SVG vectorial."""
    fig.savefig(destino / "grafica.png", dpi=EXPORT_DPI)
    fig.savefig(destino / "grafica.svg", format="svg",
                metadata={"Title": fig.texts[0].get_text(), "Date": None})
