"""Contrastes independientes del cálculo principal contra los CSV originales."""
import csv
import json
import os
import statistics
import unittest
from pathlib import Path
from urllib.request import urlopen

from matplotlib.colors import to_rgba
import pandas as pd
from PIL import Image

from grafico import ALFA_BANDA, AZUL, BENCHMARK, BUS, CONTROLES, LIMITE, META, REFERENCIA, grafico, numero


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
        self.assertTrue(self.serie.loc[:2025, "prevision"].isna().all())
        config = self.config["indicadores"]["NPRESTDOMIC"]
        for col, clave in [("meta", "metas"), ("limite", "limites")]:
            self.assertEqual(self.serie[col].to_dict(), {int(y): v for y, v in config[clave].items()})
        self.assertTrue(self.serie.naturaleza_plan.eq("Ilustrativo").all())
        self.assertEqual(list(futuro.prevision), [365118, 348660, 354793])
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
        config = self.config["indicadores"]["NPRESTDOMIC"]
        fig = grafico(self.serie, 2025, config["titulo"], config["subtitulo"],
                      "Préstamos", "Media móvil de 3 años", True)
        ax = fig.axes[0]
        barras = ax.containers
        hist = self.serie.loc[:2025]
        for linea, col, color in zip(ax.lines[:2], ("benchmark", "referencia"), (BENCHMARK, REFERENCIA)):
            self.assertEqual(list(linea.get_xdata()), list(hist.index))
            self.assertEqual(list(linea.get_ydata()), list(hist[col]))
            self.assertEqual(linea.get_color(), color)
            self.assertLess(linea.get_zorder(), barras[0].patches[0].get_zorder())
        banda, = ax.collections
        self.assertEqual(tuple(banda.get_facecolor()[0]), to_rgba(AZUL, ALFA_BANDA))
        self.assertLess(banda.get_zorder(), ax.lines[0].get_zorder())
        puntos = {tuple(p) for p in banda.get_paths()[0].vertices}
        self.assertEqual({x for x, _ in puntos}, set(hist.index))
        for y, fila in hist.iterrows():
            self.assertEqual({v for x, v in puntos if x == y}, {fila.benchmark, fila.referencia})
        for futuro, grupos in [(False, barras[:3]), (True, barras[3:])]:
            panel = self.serie.loc[2026:] if futuro else self.serie.loc[:2025]
            for grupo, col, ancho, offset, color in zip(
                grupos, ("limite", "prevision" if futuro else "bus", "meta"),
                (.18, .36, .18), (-.30, 0, .30), (LIMITE, BUS, META),
            ):
                self.assertEqual(len(grupo), len(panel))
                for (year, val), rect in zip(panel[col].items(), grupo.patches):
                    self.assertEqual(rect.get_height(), val)
                    self.assertEqual(rect.get_y(), 0)
                    self.assertAlmostEqual(rect.get_width(), ancho)
                    self.assertAlmostEqual(rect.get_x() + rect.get_width() / 2, year + offset)
                    if futuro:
                        self.assertEqual(rect.get_edgecolor(), to_rgba(color))
                        if col != "prevision":
                            self.assertEqual(rect.get_facecolor()[-1], 0)
                        else:
                            self.assertEqual(rect.get_hatch(), "///")
                    else:
                        self.assertEqual(rect.get_facecolor(), to_rgba(color))
        self.assertEqual(ax.get_ylim()[0], 0)
        self.assertEqual(len(ax.lines), 3)
        self.assertEqual(numero(435759.5), "435.759,5")
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        etiquetas = [t for t in ax.texts if hasattr(t, "xy") and t.get_visible()]
        rectangulos = [*barras[1].patches, *barras[4].patches]
        self.assertEqual(len(etiquetas), 13)
        for etiqueta, rect in zip(etiquetas, rectangulos):
            self.assertEqual(etiqueta.get_rotation(), 90)
            self.assertEqual(etiqueta.get_text(), numero(rect.get_height()))
            caja = etiqueta.get_window_extent(renderer)
            barra = rect.get_window_extent(renderer)
            self.assertTrue(barra.contains(caja.x0, caja.y0))
            self.assertTrue(barra.contains(caja.x1, caja.y1))

    def test_archivos_estaticos(self):
        html = (self.distribucion / "index.html").read_text(encoding="utf-8")
        self.assertIn("<h1>Indicadores EFQM 2028</h1>", html)
        self.assertIn('<svg ', html)
        self.assertEqual(html.count('<fieldset>'), 3)
        for opciones in CONTROLES.values():
            for serie, nombre in opciones.items():
                self.assertIn(f'name="{serie}" checked> {nombre}', html)
        self.assertIn("Descargar imagen PNG", html)
        self.assertIn("Restablecer selección", html)
        for accesorio in ["<table", "<details", "<article"]:
            self.assertNotIn(accesorio, html)
        with Image.open(self.distribucion / "grafica.png") as png:
            self.assertEqual(png.size, (3200, 1480))
        svg = (self.distribucion / "grafica.svg").read_text(encoding="utf-8")
        for contenido in [
            "Préstamos domiciliarios de material bibliográfico", "más de 40.000",
            "REBIUN Data Explorer", "mediana del grupo", "mejor resultado anual",
            "Metas y límites ilustrativos", "media móvil de 3 años", "incertidumbre",
            "350.602", "365.118", "354.793",
        ]:
            self.assertIn(contenido, svg)
