"""Comparación temporal de cinco modelos y pronóstico para el horizonte pedido."""
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import Holt, SimpleExpSmoothing


def ingenuo(y, h):
    return np.repeat(y[-1], h)


def media_movil(y, h):
    serie = list(y)
    for _ in range(h):
        serie.append(np.mean(serie[-3:]))
    return serie[-h:]


def lineal(y, h):
    x = np.arange(len(y) + h).reshape(-1, 1)
    return LinearRegression().fit(x[:-h], y).predict(x[-h:])


MODELOS = {
    "Ingenuo": ingenuo,
    "Media móvil de 3 años": media_movil,
    "Regresión lineal": lineal,
    "Suavizado exponencial simple": lambda y, h: SimpleExpSmoothing(y).fit().forecast(h),
    "Holt con tendencia amortiguada": lambda y, h: Holt(y, damped_trend=True).fit().forecast(h),
}


def evaluar(serie, horizonte):
    """Orígenes expansivos, con 5 datos iniciales y mismos cortes para cada método."""
    cortes = range(5, len(serie))
    y = serie.to_numpy(dtype=float)
    if len(cortes) < 3:
        raise ValueError("Se requieren tres orígenes como mínimo para comparar modelos")
    errores = []
    scores = []
    for nombre, modelo in MODELOS.items():
        for corte in cortes:
            h = min(horizonte, len(y) - corte)
            pred = np.asarray(modelo(y[:corte] / 1000, h)) * 1000
            if not np.isfinite(pred).all():
                raise ValueError(f"Predicción no finita: {nombre}")
            for k, valor in enumerate(np.maximum(pred, 0), 1):
                errores.append((nombre, serie.index[corte - 1], k, y[corte + k - 1], valor))
        for h in range(1, horizonte + 1):
            pares = [(real, pred) for m, _, paso, real, pred in errores if m == nombre and paso == h]
            if pares:
                real, pred = zip(*pares)
                scores.append((nombre, h, len(pares), mean_absolute_error(real, pred),
                               np.sqrt(mean_squared_error(real, pred))))
    validacion = pd.DataFrame(scores, columns=["modelo", "horizonte", "n", "mae", "rmse"])
    ranking = validacion.groupby("modelo")[["mae", "rmse"]].mean().sort_values(["mae", "rmse"])
    elegido = ranking.index[0]
    futuro = np.maximum(0, np.asarray(MODELOS[elegido](y / 1000, horizonte)) * 1000)
    detalle = pd.DataFrame(errores, columns=["modelo", "origen", "horizonte", "observado", "previsto"])
    return elegido, futuro, validacion, detalle, ranking
