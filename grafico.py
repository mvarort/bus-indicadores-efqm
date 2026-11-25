"""Composición estática y exportable de un indicador anual."""
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.path import Path
from matplotlib.ticker import FuncFormatter, MaxNLocator
from matplotlib.transforms import blended_transform_factory
import pandas as pd

LIMITE = "#512060"
BUS = "#C8102E"
META = "#388E3C"
AZUL = "#D6E7F5"
BENCHMARK = "#4682B4"
REFERENCIA = "#163D70"
ALFA_BANDA = .53
TRAZO_BENCHMARK = (0, (4, 2.5))
GRIS_INTERVALO = "#3D4751"
SIMBOLO_INTERVALO = Path([(-.32, -.5), (.32, -.5), (0, -.5), (0, .5), (-.32, .5), (.32, .5)],
                         [Path.MOVETO, Path.LINETO, Path.MOVETO, Path.LINETO, Path.MOVETO, Path.LINETO])
ROSADO = "#F8D6DC"
TINTA = "#172637"
SECUNDARIO = "#45566A"
EXPORT_DPI = 200


CONTROLES = {
    "Histórico": {"bus_actual": "Resultado BUS", "target_historical": "Meta histórica",
                  "threshold_historical": "Límite histórico"},
    "Comparaciones externas": {"benchmark": "Benchmark", "reference": "Referencia del grupo",
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
ETIQUETAS_INICIALES = {"bus_actual", "bus_forecast"}


def numero(value, decimales=None, sufijo=""):
    entero, _, fraccion = f"{value:,.{2 if decimales is None else decimales}f}".partition(".")
    if decimales is None:
        fraccion = fraccion.rstrip("0")
    return entero.replace(",", ".") + (f",{fraccion}" if fraccion else "") + sufijo


def rotular_barras(ax, valores, serie, futuro, desplazamiento, color, formato):
    """Muestra las cifras de la BUS por defecto y prepara las de meta y límite."""
    bus = serie in ETIQUETAS_INICIALES
    tinta = color if futuro else "white"
    for year, value in valores.items():
        etiqueta = ax.annotate(
            formato(value), (year + desplazamiento, value), xytext=(0, -7),
            textcoords="offset points", ha="center", va="top", rotation=90,
            fontsize=9.5 if bus else 7.5, fontweight="bold", color=tinta, zorder=7,
            visible=bus,
        )
        etiqueta.set_gid(f"etiqueta-{serie}-{year}")


def rotular_comparacion(fig, ax, hist, fut, formato, formato_intervalo, nota_intervalo):
    """Alinea dos filas de cifras históricas y predictivas bajo cada año."""
    posicion = blended_transform_factory(ax.transData, fig.transFigure)

    def fila(serie, titulo, color, valores, limites, alineacion, y, visible, formatear=formato):
        textos = [(limites, titulo, alineacion), *[
            (year, formatear(valor), "center") for year, valor in valores.dropna().items()
        ]]
        for i, (x, valor, alineacion) in enumerate(textos):
            artista = fig.text(x, y, valor, transform=posicion, color=color,
                               fontsize=7, ha=alineacion, va="center", visible=visible)
            artista.set_gid(f"etiqueta-{serie}-fila-{i}")

    x_hist = hist.index[0] - .59
    fila("benchmark", "Benchmark", BENCHMARK, hist.benchmark, x_hist, "right", .185, False)
    fila("reference", "Referencia", REFERENCIA, hist.referencia, x_hist, "right", .171, False)
    if nota_intervalo:
        x_fut = hist.index[-1] + .5
        fila("prediction_interval-inf", "IP inf.", GRIS_INTERVALO, fut.prediccion_inferior_95,
             x_fut, "center", .185, True, formato_intervalo)
        fila("prediction_interval-sup", "IP sup.", GRIS_INTERVALO, fut.prediccion_superior_95,
             x_fut, "center", .171, True, formato_intervalo)


def grafico(panel, fin, titulo, subtitulo, unidad, modelo, ilustrativos,
            decimales=0, maximo=None, notas_indicador=(), polaridad="creciente", unidad_porcentual=False, nota_intervalo=None, periodo_ajuste=None):
    sufijo = " %" if unidad_porcentual else ""
    def formato(valor):
        return numero(valor, decimales, sufijo)

    def formato_comparacion(valor):
        return numero(valor, decimales or None, sufijo)
    """Dibuja zonas comparativas, barras y notas utilizando los valores del CSV."""
    fig = Figure(figsize=(16, 7.4), facecolor="white")
    fig.set_label(titulo)
    FigureCanvasAgg(fig)
    ax = fig.add_axes([.072, .228, .908, .511])
    hist = panel.loc[:fin]
    fut = panel.loc[fin + 1:]
    banda = ax.fill_between(hist.index, hist.benchmark, hist.referencia,
                           color=AZUL, alpha=ALFA_BANDA, linewidth=0, zorder=1)
    banda.set_gid("serie-comparison_band-historico")
    referencias = {}
    for serie, columna, nombre, color, trazo in [
        ("benchmark", "benchmark", "Benchmark", BENCHMARK, TRAZO_BENCHMARK),
        ("reference", "referencia", "Referencia del grupo", REFERENCIA, "-"),
    ]:
        linea, = ax.plot(
            hist.index, hist[columna], label=nombre, color=color, linestyle=trazo,
            linewidth=1.1, marker="o", markersize=4, markerfacecolor="white",
            markeredgecolor=color, markeredgewidth=.85, zorder=4,
        )
        linea.set_gid(f"serie-{serie}-historico")
        referencias[serie] = linea

    lideres = hist.loc[hist.bus_lider.eq(True).fillna(False)]
    if not lideres.empty:
        destacados, = ax.plot(
            lideres.index, lideres.referencia, linestyle="none", marker="o", markersize=4,
            markerfacecolor=BUS, markeredgecolor=REFERENCIA, markeredgewidth=.85, zorder=5,
        )
        destacados.set_gid("serie-reference-liderazgo")

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
            rotular_barras(ax, valores, serie, futuro, desplazamiento, color, formato)

    rotular_comparacion(fig, ax, hist, fut, formato_comparacion, formato, nota_intervalo)

    columnas_escala = ["bus", "benchmark", "referencia", "prevision", "limite", "meta"]
    if nota_intervalo:
        intervalos = fut[["prediccion_inferior_95", "prediccion_superior_95"]].dropna()
        for year, lo, hi in intervalos.itertuples():
            linea, = ax.plot(
                [year-.075, year+.075, float("nan"), year, year, float("nan"), year-.075, year+.075],
                [lo, lo, float("nan"), lo, hi, float("nan"), hi, hi],
                color=GRIS_INTERVALO, linewidth=.8, zorder=6,
            )
            linea.set_gid(f"serie-prediction_interval-{year}")
        columnas_escala.append("prediccion_superior_95")
    if nota_intervalo is not None:
        puntos, = ax.plot(fut.index, fut.prevision, linestyle="none", marker="o",
                          markersize=4, markerfacecolor="white", markeredgecolor=GRIS_INTERVALO,
                          markeredgewidth=.85, zorder=6.5)
        puntos.set_gid("serie-bus_forecast-punto")

    superior = panel[columnas_escala].max().max()
    ax.set_ylim(0, maximo if maximo is not None else max(superior * 1.13, 1e-9))
    ax.set_xlim(panel.index[0] - .52, panel.index[-1] + .52)
    ax.set_xticks(panel.index, [str(y) for y in panel.index], fontsize=9, fontweight="medium")
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6, steps=[1, 2, 2.5, 5, 10]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: numero(value, decimales if decimales and not unidad_porcentual else None, sufijo)))
    ax.tick_params(axis="both", length=0, pad=8, colors=SECUNDARIO, labelsize=9)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#DFE5EC", linewidth=.65)
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
        ("benchmark", referencias["benchmark"]),
        ("reference", referencias["reference"]),
        ("comparison_band", Patch(facecolor=AZUL, alpha=ALFA_BANDA, label="Banda comparativa")),
    ]
    if nota_intervalo:
        elementos.append(("prediction_interval", Line2D(
            [], [], color=GRIS_INTERVALO, linestyle="none", marker=SIMBOLO_INTERVALO,
            markersize=10, markeredgewidth=.8, label="Intervalo de predicción (95 %)",
        )))
    leyenda = fig.legend(handles=[handle for _, handle in elementos],
                         loc="upper left", bbox_to_anchor=(.047, .842),
                         borderaxespad=0, ncols=len(elementos), frameon=False, fontsize=9.5,
                         columnspacing=1.65, handlelength=1.6, labelcolor=TINTA)
    for (serie, _), muestra, etiqueta in zip(elementos, leyenda.legend_handles, leyenda.get_texts()):
        muestra.set_gid(f"leyenda-{serie}-muestra")
        etiqueta.set_gid(f"leyenda-{serie}-texto")

    fig.add_artist(Line2D([.047, .98], [.155, .155], transform=fig.transFigure,
                          color="#DFE5EC", linewidth=.7))
    descripcion_referencia = "máximo descriptivo anual" if polaridad == "pendiente" else "mejor resultado anual"
    periodo = f" · ajuste {periodo_ajuste}" if periodo_ajuste else ""
    notas = [
        ("fuente", "Fuente  REBIUN Data Explorer."),
        ("comparacion", f"Benchmark: mediana del grupo comparador, excluida la BUS. Referencia del grupo: {descripcion_referencia}, incluida la BUS. "
         "Banda comparativa: intervalo comprendido entre ambas referencias."),
        ("banda", "La banda no es un intervalo de confianza estadístico ni una zona de excelencia."),
        ("plan", "Metas y límites ilustrativos." if ilustrativos else "Metas y límites oficiales."),
        ("prevision", f"Previsión mediante {modelo.lower()}{periodo}. Estimaciones sujetas a incertidumbre."),
    ]
    if nota_intervalo:
        notas.append(("intervalo", "Intervalo de predicción del 95 % nominal (remates grises). Cobertura sin calibrar con esta muestra."))
    elif nota_intervalo is not None:
        notas.append(("sin-intervalo", "Sin intervalo del 95 % defendible con los datos del periodo de ajuste."))
    if not lideres.empty:
        notas.append(("liderazgo", "Círculo rojo: la BUS alcanza el mejor resultado anual, incluidos los empates."))
    notas.extend((f"indicador-{i}", nota) for i, nota in enumerate(notas_indicador))
    separacion_notas = min(.023, .112 / max(1, len(notas) - 1))
    for i, (clave, nota) in enumerate(notas):
        artista = fig.text(.048, .132 - i * separacion_notas, nota, fontsize=9, color=SECUNDARIO, va="top")
        artista.set_gid(f"nota-{clave}")
    return fig


def exportar(fig, destino, sufijo=""):
    """Exporta la misma composición al PNG principal y al SVG vectorial."""
    fig.savefig(destino / f"grafica{sufijo}.png", dpi=EXPORT_DPI)
    opcionales = [artista for artista in [*fig.texts, *fig.axes[0].texts]
                  if (artista.get_gid() or "").startswith("etiqueta-") and not artista.get_visible()]
    for artista in opcionales:
        artista.set_visible(True)
    ruta_svg = destino / f"grafica{sufijo}.svg"
    fig.savefig(ruta_svg, format="svg", metadata={"Title": fig.get_label(), "Date": None})
    svg = ruta_svg.read_text(encoding="utf-8")
    for artista in opcionales:
        grupo = f'<g id="{artista.get_gid()}"'
        svg = svg.replace(grupo + ">", grupo + ' style="display:none">', 1)
        artista.set_visible(False)
    ruta_svg.write_text(svg, encoding="utf-8")
