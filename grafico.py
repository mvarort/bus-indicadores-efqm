"""Composición estática y exportable de un indicador anual."""
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
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
    fondo = ROSADO if serie == "bus_forecast" else "white"
    if futuro or not bus:
        tinta = "#85122A" if bus else color
        caja = dict(facecolor=fondo, edgecolor="none", boxstyle="round,pad=.18")
    else:
        tinta, caja = "white", None
    for year, value in valores.items():
        etiqueta = ax.annotate(
            formato(value), (year + desplazamiento, value), xytext=(0, -7),
            textcoords="offset points", ha="center", va="top", rotation=90,
            fontsize=9.5 if bus else 7.5, fontweight="bold", color=tinta, bbox=caja, zorder=7,
            visible=bus,
        )
        etiqueta.set_gid(f"etiqueta-{serie}-{year}")


def rotular_comparacion(fig, ax, hist, formato):
    """Alinea los valores opcionales debajo de cada año sin tapar las series."""
    posicion = blended_transform_factory(ax.transData, fig.transFigure)
    filas = [
        ("benchmark", "Benchmark", BENCHMARK, hist.benchmark.map(formato, na_action="ignore")),
        ("reference", "Referencia", REFERENCIA, hist.referencia.map(formato, na_action="ignore")),
        ("comparison_band", "Banda", REFERENCIA, {
            year: f"{formato(min(mediana, mejor))}–{formato(max(mediana, mejor))}"
            for year, mediana, mejor in hist[["benchmark", "referencia"]].dropna().itertuples()
        }),
    ]
    for orden, (serie, titulo, color, valores) in enumerate(filas):
        y = .185 - orden * .012
        textos = [(hist.index[0] - .59, titulo, "right"), *[
            (year, valor, "center") for year, valor in valores.items() if pd.notna(valor)
        ]]
        for i, (x, valor, alineacion) in enumerate(textos):
            artista = fig.text(x, y, valor, transform=posicion, color=color,
                               fontsize=6.4, ha=alineacion, va="center", visible=False)
            artista.set_gid(f"etiqueta-{serie}-fila-{i}")


def grafico(panel, fin, titulo, subtitulo, unidad, modelo, ilustrativos,
            decimales=0, maximo=None, notas_indicador=(), polaridad="creciente", unidad_porcentual=False):
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
                           color=AZUL, alpha=ALFA_BANDA, linewidth=0, zorder=0)
    banda.set_gid("serie-comparison_band-historico")
    for serie, columna, color, trazo in [
        ("benchmark", "benchmark", BENCHMARK, TRAZO_BENCHMARK),
        ("reference", "referencia", REFERENCIA, "-"),
    ]:
        linea, = ax.plot(hist.index, hist[columna], color=color, linewidth=1.65, linestyle=trazo, zorder=2)
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
            rotular_barras(ax, valores, serie, futuro, desplazamiento, color, formato)

    rotular_comparacion(fig, ax, hist, formato_comparacion)

    superior = panel[["bus", "benchmark", "referencia", "prevision", "limite", "meta"]].max().max()
    ax.set_ylim(0, maximo if maximo is not None else max(superior * 1.13, 1e-9))
    ax.set_xlim(panel.index[0] - .52, panel.index[-1] + .52)
    ax.set_xticks(panel.index, [str(y) for y in panel.index], fontsize=9, fontweight="medium")
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6, steps=[1, 2, 2.5, 5, 10]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: numero(value, decimales if decimales and not unidad_porcentual else None, sufijo)))
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
        ("benchmark", Line2D([], [], color=BENCHMARK, linewidth=1.65, linestyle=TRAZO_BENCHMARK, label="Benchmark")),
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
    descripcion_referencia = "máximo descriptivo anual" if polaridad == "pendiente" else (
        "menor resultado anual" if polaridad == "decreciente" else "mejor resultado anual"
    )
    notas = [
        ("fuente", "Fuente  REBIUN Data Explorer."),
        ("comparacion", f"Benchmark: mediana del grupo comparador. Referencia del grupo: {descripcion_referencia}. "
         "Banda comparativa: intervalo comprendido entre ambas referencias."),
        ("banda", "La banda no es un intervalo de confianza estadístico ni una zona de excelencia."),
        ("plan", "Metas y límites ilustrativos." if ilustrativos else "Metas y límites oficiales."),
        ("prevision", f"Previsión mediante {modelo.lower()}. Estimaciones sujetas a incertidumbre, sin intervalo calibrado."),
    ]
    notas.extend((f"indicador-{i}", nota) for i, nota in enumerate(notas_indicador))
    separacion_notas = .020 if notas_indicador else .023
    for i, (clave, nota) in enumerate(notas):
        artista = fig.text(.048, .132 - i * separacion_notas, nota, fontsize=9, color=SECUNDARIO, va="top")
        artista.set_gid(f"nota-{clave}")
    return fig


def exportar(fig, destino):
    """Exporta la misma composición al PNG principal y al SVG vectorial."""
    fig.savefig(destino / "grafica.png", dpi=EXPORT_DPI)
    opcionales = [artista for artista in [*fig.texts, *fig.axes[0].texts]
                  if (artista.get_gid() or "").startswith("etiqueta-") and not artista.get_visible()]
    for artista in opcionales:
        artista.set_visible(True)
    ruta_svg = destino / "grafica.svg"
    fig.savefig(ruta_svg, format="svg", metadata={"Title": fig.get_label(), "Date": None})
    svg = ruta_svg.read_text(encoding="utf-8")
    for artista in opcionales:
        grupo = f'<g id="{artista.get_gid()}"'
        svg = svg.replace(grupo + ">", grupo + ' style="display:none">', 1)
        artista.set_visible(False)
    ruta_svg.write_text(svg, encoding="utf-8")
