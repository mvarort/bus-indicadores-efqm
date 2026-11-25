"""Adquisición de una revisión pública fija y agregación anual REBIUN."""
from pathlib import Path

import numpy as np
import pandas as pd

ID = "Codigo_Biblioteca_REBIUN"
KEY = ["Anio", ID]


def cargar(config, carpeta=None):
    def leer(nombre, **kwargs):
        base = config["fuente"].replace("github.com", "raw.githubusercontent.com")
        ruta = Path(carpeta) / nombre if carpeta else f"{base}/{config['revision']}/data/{nombre}"
        return pd.read_csv(ruta, sep=";", encoding="utf-8-sig", dtype={ID: str}, **kwargs)

    datos = leer("rebiun_real.csv", usecols=KEY + ["Codigo_Tecnico", "Valor"])
    centros = leer("bibliotecas_rebiun.csv", usecols=[ID, "Biblioteca", "Modalidad"])
    return datos, centros


def preparar(datos, centros, config, codigo):
    """Preserva los elegibles sin dato y calcula los extremos sobre casos válidos."""
    years = range(config["inicio"], config["fin"] + 1)
    indicador = config["indicadores"][codigo]
    formula = indicador.get("formula")
    variables = {formula["numerador"], formula["denominador"]} if formula else {indicador.get("variable", codigo)}
    subset = datos.loc[datos.Anio.isin(years) &
                      datos.Codigo_Tecnico.isin(variables | {"NUSUARIOPROP"})].copy()
    subset["Valor"] = pd.to_numeric(subset.Valor, errors="raise")
    conocidos = subset.Valor.dropna()
    if not np.isfinite(conocidos).all() or (conocidos < 0).any():
        raise ValueError("Se requieren valores finitos y no negativos")
    if set(subset[ID]) - set(centros[ID]):
        raise ValueError("Hay códigos REBIUN sin entrada en el directorio")
    panel = subset.pivot(index=KEY, columns="Codigo_Tecnico", values="Valor").reset_index()
    if formula:
        numerador = panel[formula["numerador"]]
        denominador = panel[formula["denominador"]]
        panel[codigo] = numerador.div(denominador.where(denominador.gt(0))) * formula["factor"]
    else:
        panel[codigo] = panel[indicador.get("variable", codigo)]
    minimo, maximo = indicador.get("limites_naturales", [0, None])
    valido = np.isfinite(panel[codigo]) & panel[codigo].ge(minimo)
    if maximo is not None:
        valido &= panel[codigo].le(maximo)
    panel[codigo] = panel[codigo].where(valido)
    panel = panel.merge(centros, on=ID, validate="many_to_one")
    bus = panel.loc[panel[ID].eq(config["biblioteca"])].set_index("Anio")[codigo].reindex(years)
    if bus.isna().any():
        raise ValueError("La serie BUS debe estar completa para ajustar la previsión")
    miembros = panel.loc[
        panel.Modalidad.eq("Presencial") &
        panel.NUSUARIOPROP.gt(config["umbral_usuarios"]) &
        panel[ID].ne(config["biblioteca"])
    ].copy().sort_values(["Anio", "Biblioteca"])
    grupo = miembros.groupby("Anio")[codigo]
    polaridad = indicador["mejor"]
    if polaridad not in {"max", "min"}:
        raise ValueError(f"{codigo}: la polaridad debe ser max o min")
    extremo_externo = grupo.max() if polaridad == "max" else grupo.min()
    candidatos = pd.concat([extremo_externo, bus], axis=1)
    mejor = candidatos.max(axis=1) if polaridad == "max" else candidatos.min(axis=1)
    bus_lider = bus.eq(mejor) & (indicador["polaridad"] != "pendiente")
    miembros["referencia"] = miembros[codigo].notna() & miembros[codigo].eq(miembros.Anio.map(mejor))
    return pd.DataFrame({
        "bus": bus, "benchmark": grupo.median(), "referencia": mejor,
        "elegibles": grupo.size(), "con_dato": grupo.count(), "bus_lider": bus_lider.astype("boolean"),
    }).reindex(years), miembros
