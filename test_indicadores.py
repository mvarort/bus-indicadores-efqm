"""Contrastes independientes del cálculo principal contra los CSV originales."""
import csv
import json
import os
import statistics
import unittest
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

from grafico import grafico, numero


class Indicadores(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(Path("indicadores.json").read_text())
        cls.distribucion = Path("site/NPRESTDOMIC")
        cls.serie = pd.read_csv(cls.distribucion / "serie.csv", index_col="Anio", sep=";", decimal=",")
        cls.grupo = pd.read_csv(cls.distribucion / "grupo.csv", sep=";", decimal=",",
                               dtype={"Codigo_Biblioteca_REBIUN": str})
        base = f"https://raw.githubusercontent.com/mvarort/datos-rebiun/{cls.config['revision']}/data"

        def filas(nombre):
            local = os.getenv("REBIUN_DATOS")
            if local:
                contenido = (Path(local) / nombre).read_text(encoding="utf-8-sig")
            else:
                with urlopen(f"{base}/{nombre}", timeout=30) as response:
                    contenido = response.read().decode("utf-8-sig")
            return list(csv.DictReader(contenido.splitlines(), delimiter=";"))

        cls.presenciales = {r["Codigo_Biblioteca_REBIUN"] for r in filas("bibliotecas_rebiun.csv")
                            if r["Modalidad"] == "Presencial"}
        cls.original = {(int(r["Anio"]), r["Codigo_Biblioteca_REBIUN"], r["Codigo_Tecnico"]): float(r["Valor"])
                        for r in filas("rebiun_real.csv")
                        if r["Codigo_Tecnico"] in {"NPRESTDOMIC", "NUSUARIOPROP"} and r["Valor"]}

    def test_contraste_de_todos_los_anios(self):
        for year in range(2016, 2026):
            with self.subTest(year=year):
                ids = {centro for centro in self.presenciales - {"67"}
                       if self.original.get((year, centro, "NUSUARIOPROP"), 0) > 40000}
                datos = {centro: self.original[(year, centro, "NPRESTDOMIC")] for centro in ids
                         if (year, centro, "NPRESTDOMIC") in self.original}
                grupo = self.grupo[self.grupo.Anio.eq(year)]
                self.assertEqual(set(grupo.Codigo_Biblioteca_REBIUN), ids)
                self.assertEqual(set(grupo.loc[grupo.referencia, "Codigo_Biblioteca_REBIUN"]),
                                 {centro for centro, val in datos.items() if val == max(datos.values())})
                row = self.serie.loc[year]
                self.assertEqual(row.bus, self.original[(year, "67", "NPRESTDOMIC")])
                self.assertEqual(row.elegibles, len(ids))
                self.assertEqual(row.con_dato, len(datos))
                self.assertEqual(row.benchmark, statistics.median(datos.values()))
                self.assertEqual(row.referencia, max(datos.values()))

    def test_prevision_metas_y_validacion(self):
        futuro = self.serie.loc[2026:2028]
        self.assertTrue(futuro[["bus", "benchmark", "referencia"]].isna().all().all())
        self.assertTrue(self.serie.loc[:2025, ["prevision", "meta", "limite"]].isna().all().all())
        self.assertEqual(list(futuro.prevision), [365118, 348660, 354793])
        html = (self.distribucion / "index.html").read_text()
        self.assertIn("<strong>365.118</strong><small>Previsión central", html)
        self.assertTrue(futuro.naturaleza_plan.eq("Ilustrativo").all())
        errores = pd.read_csv(self.distribucion / "errores-validacion.csv", sep=";", decimal=",")
        metricas = pd.read_csv(self.distribucion / "validacion.csv", sep=";", decimal=",")
        self.assertEqual(len(metricas), 15)
        for fila in metricas.itertuples():
            casos = errores.loc[(errores.modelo == fila.modelo) & (errores.horizonte == fila.horizonte)]
            self.assertEqual(len(casos), 6 - fila.horizonte)
            self.assertTrue(all(real == self.serie.loc[origen + fila.horizonte, "bus"]
                                for origen, real in zip(casos.origen, casos.observado)))
            delta = casos.observado - casos.previsto
            self.assertAlmostEqual(fila.mae, statistics.mean(abs(delta)), places=7)
            self.assertAlmostEqual(fila.rmse, statistics.mean(delta ** 2) ** .5, places=7)
        self.assertEqual(metricas.groupby("modelo").mae.mean().idxmin(), "Media móvil de 3 años")

    def test_notacion_visual(self):
        fig = grafico(self.serie, 2025, "Préstamos", True)
        banda, limite, bus, prevision, meta = fig.data
        self.assertEqual((limite.width, bus.width, meta.width), (.2, .4, .2))
        self.assertLess(limite.x[0], prevision.x[0])
        self.assertGreater(meta.x[0], prevision.x[0])
        self.assertEqual(prevision.marker.pattern.shape, "/")
        self.assertEqual(limite.marker.line.color, "#512060")
        self.assertEqual(meta.marker.line.color, "#388E3C")
        self.assertEqual(max(banda.x), 2025)
        self.assertEqual(fig.layout.yaxis.range[0], 0)
        self.assertEqual(numero(435759.5), "435.759,5")
