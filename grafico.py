"""Gráfico Plotly con posiciones explícitas y etiquetas en formato español."""
import pandas as pd
import plotly.graph_objects as go


def numero(value):
    if pd.isna(value):
        return "Sin dato"
    entero, _, decimales = f"{value:,.2f}".partition(".")
    fraccion = decimales.rstrip("0")
    return entero.replace(",", ".") + (f",{fraccion}" if fraccion else "")


def grafico(panel, fin, unidad, ilustrativos):
    fig = go.Figure()
    hist = panel.loc[:fin]
    fut = panel.loc[fin + 1:]
    texto = " ilustrativo" if ilustrativos else ""
    banda = hist.dropna(subset=["benchmark", "referencia"])
    fig.add_bar(
        name="Mediana → referencia del grupo", x=banda.index, width=.88,
        base=banda.benchmark, y=banda.referencia - banda.benchmark,
        marker=dict(color="rgba(76,146,199,0.24)"),
        customdata=[[numero(row.benchmark), numero(row.referencia), int(row.con_dato)]
                    for row in banda.itertuples()],
        hovertemplate="Mediana %{customdata[0]}<br>Referencia %{customdata[1]}"
                      "<br>Bibliotecas con dato %{customdata[2]}<extra></extra>",
    )
    series = [
        (panel, "limite", "Límite" + texto, "#512060", -.31, .20, "outline"),
        (hist, "bus", "BUS observado", "#C8102E", 0, .40, "solid"),
        (fut, "prevision", "BUS previsto", "#C8102E", 0, .40, "pattern"),
        (panel, "meta", "Meta" + (" ilustrativa" if ilustrativos else ""), "#388E3C", .31, .20, "outline"),
    ]
    for data, col, name, color, shift, width, style in series:
        values = data[col].dropna()
        marker = dict(color=color)
        if style == "outline":
            marker = dict(color="rgba(0,0,0,0)", line=dict(color=color, width=2))
        if style == "pattern":
            marker = dict(color=color, pattern=dict(shape="/", fgcolor=color, bgcolor="#F4CBD3",
                                                   fillmode="replace", solidity=.22))
        show_text = col in ("bus", "prevision")
        fig.add_bar(
            name=name, x=values.index + shift, y=values, width=width, marker=marker,
            customdata=[[int(year), numero(value)] for year, value in values.items()],
            text=[numero(value) for value in values] if show_text else None,
            textposition="outside" if show_text else "none",
            textfont=dict(size=12, color="#172637"), cliponaxis=False,
            hovertemplate="%{customdata[0]} · %{customdata[1]}<extra>%{fullData.name}</extra>",
        )
    top = panel[["bus", "referencia", "prevision", "limite", "meta"]].max().max()
    fig.add_vrect(x0=fin + .5, x1=panel.index[-1] + .5, fillcolor="#F7F3F6",
                  line_width=0, layer="below")
    fig.add_vline(x=fin + .5, line_dash="dot", line_color="#817584", line_width=1)
    fig.add_annotation(x=(panel.index[0]+fin)/2, y=1.05, yref="paper", text="Histórico", showarrow=False)
    fig.add_annotation(x=(fin+1+panel.index[-1])/2, y=1.05, yref="paper", text="Prospectiva", showarrow=False)
    fig.update_layout(
        barmode="overlay", height=520, margin=dict(l=70, r=20, t=42, b=100),
        font=dict(family="system-ui, sans-serif", color="#233348"),
        paper_bgcolor="#fff", plot_bgcolor="#fff", separators=",. ",
        legend=dict(orientation="h", y=-.13, title_text=""),
        xaxis=dict(tickmode="array", tickvals=list(panel.index), showgrid=False,
                   range=[panel.index[0]-.5, panel.index[-1]+.5], fixedrange=True),
        yaxis=dict(range=[0, top*1.18], gridcolor="#E3E9EF", separatethousands=True,
                   tickformat=",.0f", title=unidad, fixedrange=True),
    )
    return fig
