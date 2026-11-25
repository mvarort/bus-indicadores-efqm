"""Intervalos predictivos marginales para un nuevo resultado anual."""
import numpy as np
import pandas as pd
from scipy.stats import t
from statsmodels.tsa.holtwinters import SimpleExpSmoothing

from prevision import MODELOS
from revision_predictiva import invertir, transformar

NIVEL = .95

METODOS = {
    "Regresión lineal": "t de Student para una nueva observación en regresión lineal.",
    "Media móvil de 3 años": "Innovaciones aditivas propagadas por la recursión de la media móvil.",
    "Suavizado exponencial simple": "Innovaciones aditivas del modelo de nivel, con parámetros fijos tras el ajuste.",
    "Ingenuo": "Innovaciones de un paseo aleatorio sin deriva.",
}


def intervalo(modelo, y, horizonte, limites):
    """Usa la misma media predictiva puntual y devuelve extremos sin redondear."""
    n = len(y)
    pasos = np.arange(1, horizonte + 1)
    if modelo == "Regresión lineal":
        x = np.arange(n)
        residuos = y - np.polyval(np.polyfit(x, y, 1), x)
        gl = n - 2
        factor = 1 + 1/n + ((n - 1 + pasos) - x.mean())**2 / np.sum((x - x.mean())**2)
    elif modelo == "Media móvil de 3 años":
        residuos = y[3:] - np.convolve(y, np.ones(3)/3, mode="valid")[:-1]
        gl = len(residuos)
        respuesta = [0., 0., 1.]
        for _ in range(1, horizonte):
            respuesta.append(np.mean(respuesta[-3:]))
        factor = np.cumsum(np.square(respuesta[2:]))
    elif modelo == "Suavizado exponencial simple":
        ajuste = SimpleExpSmoothing(y).fit()
        residuos = ajuste.resid
        gl = n - 2
        factor = 1 + (pasos - 1) * ajuste.params["smoothing_level"]**2
    elif modelo == "Ingenuo":
        residuos = np.diff(y)
        gl = len(residuos)
        factor = pasos
    else:
        return np.full((horizonte, 2), np.nan)
    if gl < 3:
        return np.full((horizonte, 2), np.nan)
    varianza = np.sum(np.square(residuos)) / gl
    if not np.isfinite(varianza) or varianza <= 0:
        return np.full((horizonte, 2), np.nan)
    margen = t.ppf((1 + NIVEL)/2, gl) * np.sqrt(varianza * factor)
    centro = np.asarray(MODELOS[modelo](y, horizonte))
    extremos = np.column_stack((centro - margen, centro + margen))
    return np.clip(extremos, *limites) if limites != (None, None) else extremos


def evaluar_intervalos(serie, modelo, horizonte, limites, entrenamiento_minimo, escala_ajuste,
                       transformacion="identidad"):
    """Evalúa el modelo elegido en orígenes expansivos y separa los no estimables."""
    y = serie.to_numpy(dtype=float) / escala_ajuste
    limites_escalados = tuple(v / escala_ajuste if v is not None else None for v in limites)
    y = transformar(y, transformacion, limites_escalados)
    dominio = limites_escalados if transformacion == "identidad" else (None, None)

    def extremos_en_unidades(muestra, pasos):
        extremos = intervalo(modelo, muestra, pasos, dominio)
        return invertir(extremos, transformacion, limites_escalados) * escala_ajuste

    final = extremos_en_unidades(y, horizonte)
    filas = []
    for corte in range(entrenamiento_minimo, len(y)):
        h = min(horizonte, len(y) - corte)
        extremos = extremos_en_unidades(y[:corte], h)
        for paso, (inf, sup) in enumerate(extremos, 1):
            real = serie.iloc[corte + paso - 1]
            cubierto = bool(inf <= real <= sup) if np.isfinite(inf) and np.isfinite(sup) else None
            filas.append((serie.index[corte - 1], paso, real, inf, sup, cubierto))
    detalle = pd.DataFrame(filas, columns=["origen", "horizonte", "observado", "inferior", "superior", "cubierto"])
    resumen = detalle.groupby("horizonte").cubierto.agg(
        disponibles="size", estimables="count",
        cubiertos=lambda valores: int(valores.dropna().sum()),
    ).reindex(range(1, horizonte + 1), fill_value=0)
    resumen["cobertura"] = resumen.cubiertos.div(resumen.estimables.where(resumen.estimables.gt(0)))
    return final, detalle, resumen
