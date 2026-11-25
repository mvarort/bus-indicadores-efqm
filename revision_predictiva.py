"""Comparación de ventanas, transformaciones e intervención en escala original."""
import numpy as np
import pandas as pd
from scipy.special import expit, logit

from prevision import MODELOS

CAMBIO_NIVEL = "Cambio de nivel"
MINIMOS_RECIENTE = dict(zip(MODELOS, (2, 3, 3, 3, 5)))


def transformar(y, transformacion, limites):
    if transformacion == "log":
        if np.any(y <= 0):
            raise ValueError("La transformación log exige valores positivos")
        return np.log(y)
    if transformacion == "logit":
        minimo, maximo = limites
        proporcion = (y - minimo) / (maximo - minimo)
        if np.any((proporcion <= 0) | (proporcion >= 1)):
            raise ValueError("La transformación logit exige valores interiores al dominio")
        return logit(proporcion)
    return y


def invertir(y, transformacion, limites):
    if transformacion == "log":
        return np.exp(y)
    if transformacion == "logit":
        minimo, maximo = limites
        return minimo + (maximo - minimo) * expit(y)
    return y


def pronosticar(serie, modelo, horizonte, limites, escala, transformacion="identidad", ruptura=None):
    y = transformar(serie.to_numpy(dtype=float) / escala, transformacion,
                    tuple(v / escala if v is not None else None for v in limites))
    if modelo == CAMBIO_NIVEL:
        posterior = serie.index >= ruptura
        if min(posterior.sum(), (~posterior).sum()) < 2:
            raise ValueError("Se requieren dos observaciones por régimen")
        puntual = np.repeat(y[posterior].mean(), horizonte)
    else:
        puntual = MODELOS[modelo](y, horizonte)
    valores = invertir(np.asarray(puntual), transformacion,
                       tuple(v / escala if v is not None else None for v in limites)) * escala
    return np.clip(valores, *limites)


def candidatos(serie, config):
    inicio = int(serie.index[0])
    reciente = config["inicio_reciente"]
    minimo = config["entrenamiento_minimo"]
    for modelo in MODELOS:
        yield "Completa", modelo, inicio, minimo, "identidad", None
        yield "Reciente", modelo, reciente, MINIMOS_RECIENTE[modelo], "identidad", None
    for modelo in config["modelos_transformados"]:
        yield "Transformada", modelo, inicio, minimo, config["transformacion_alternativa"], None
    if ruptura := config.get("cambio_nivel"):
        yield "Cambio de nivel", CAMBIO_NIVEL, inicio, minimo, "identidad", ruptura


def estudiar(serie, horizonte, limites, config):
    """Exporta errores por origen, métricas y previsiones de candidatos estimables."""
    errores, futuros, catalogo = [], [], []
    escala = config["escala_ajuste"]
    for escenario, modelo, inicio, minimo, transformacion, ruptura in candidatos(serie, config):
        historial = serie.loc[inicio:]
        apto = len(historial) >= minimo
        catalogo.append((escenario, modelo, transformacion, inicio, int(serie.index[-1]),
                         len(historial), minimo, ruptura, apto))
        if not apto:
            continue
        pred = pronosticar(historial, modelo, horizonte, limites, escala, transformacion, ruptura)
        futuros.extend((escenario, modelo, paso, valor) for paso, valor in enumerate(pred, 1))
        for corte in range(minimo, len(historial)):
            muestra = historial.iloc[:corte]
            origen = int(muestra.index[-1])
            if ruptura and origen < ruptura + 1:
                continue
            h = min(horizonte, len(historial) - corte)
            previsto = pronosticar(muestra, modelo, h, limites, escala, transformacion, ruptura)
            errores.extend((escenario, modelo, origen, len(muestra), paso,
                             historial.iloc[corte + paso - 1], valor)
                            for paso, valor in enumerate(previsto, 1))
    detalle = pd.DataFrame(errores, columns=["escenario", "modelo", "origen", "n_ajuste",
                                            "horizonte", "observado", "previsto"])
    delta = detalle.previsto - detalle.observado
    detalle = detalle.assign(absoluto=delta.abs(), cuadrado=delta.pow(2))
    comparaciones = {
        "disponibles": detalle,
        "origen_comun_reciente": detalle.loc[detalle.origen.eq(2024)],
        "origenes_2022_2024": detalle.loc[detalle.origen.ge(2022)],
    }
    metricas = []
    for comparacion, tabla in comparaciones.items():
        resumen = tabla.groupby(["escenario", "modelo", "horizonte"]).agg(
            n=("absoluto", "size"), mae=("absoluto", "mean"), mse=("cuadrado", "mean"),
        ).reset_index()
        resumen["rmse"] = np.sqrt(resumen.pop("mse"))
        resumen["comparacion"] = comparacion
        metricas.append(resumen)
    return (
        pd.DataFrame(catalogo, columns=["escenario", "modelo", "transformacion", "inicio", "fin",
                                        "n_ajuste", "minimo_ajuste", "ruptura", "estimable"]),
        detalle,
        pd.concat(metricas, ignore_index=True),
        pd.DataFrame(futuros, columns=["escenario", "modelo", "horizonte", "previsto"]),
    )
