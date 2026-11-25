"""Contrastes independientes del cálculo principal contra los CSV originales."""
import csv
from copy import deepcopy
import json
import os
import statistics
import unittest
from pathlib import Path
from urllib.request import urlopen

from matplotlib.colors import to_rgba
import numpy as np
import pandas as pd
import statsmodels.api as sm
from PIL import Image

from datos import ID, preparar
from intervalos import intervalo
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
                        if r["Codigo_Tecnico"] in {"NPRESTDOMIC", "NUSUARIOPROP", "NMONPAGOLIC", "NPUESTOSLECT",
                                                  "GASTOINFOELECT", "GASTORECINFO"} and r["Valor"]}

    def test_contraste_de_todos_los_anios(self):
        for year in range(2016, 2026):
            with self.subTest(year=year):
                ids = {centro for centro in self.presenciales - {"67"}
                       if self.original.get((year, centro, "NUSUARIOPROP"), 0) > 40000}
                datos = {centro: self.original[(year, centro, "NPRESTDOMIC")] for centro in ids
                         if (year, centro, "NPRESTDOMIC") in self.original}
                grupo = self.grupo[self.grupo.Anio.eq(year)]
                self.assertEqual(set(grupo.Codigo_Biblioteca_REBIUN), ids)
                row = self.serie.loc[year]
                mejor = max(row.bus, *datos.values())
                self.assertEqual(set(grupo.loc[grupo.referencia, "Codigo_Biblioteca_REBIUN"]),
                                 {centro for centro, val in datos.items() if val == mejor})
                self.assertEqual(row.bus, self.original[(year, "67", "NPRESTDOMIC")])
                self.assertEqual(row.elegibles, len(ids))
                self.assertEqual(row.con_dato, len(datos))
                self.assertEqual(row.benchmark, statistics.median(datos.values()))
                self.assertEqual(row.referencia, mejor)
                self.assertEqual(row.bus_lider, row.bus == mejor)

    def test_polaridad_decreciente(self):
        config = deepcopy(self.config)
        config["indicadores"]["NPRESTDOMIC"].update(mejor="min", polaridad="decreciente")
        datos = pd.DataFrame(
            [(year, centro, codigo, valor) for (year, centro, codigo), valor in self.original.items()
             if centro in self.presenciales],
            columns=["Anio", ID, "Codigo_Tecnico", "Valor"],
        )
        centros = pd.DataFrame([(centro, centro, "Presencial") for centro in sorted(self.presenciales)],
                               columns=[ID, "Biblioteca", "Modalidad"])
        calculado, miembros = preparar(datos, centros, config, "NPRESTDOMIC")
        for year, fila in calculado.iterrows():
            datos_anuales = miembros.loc[miembros.Anio.eq(year)]
            self.assertEqual(fila.referencia, min(fila.bus, datos_anuales.NPRESTDOMIC.min()))
            self.assertLessEqual(fila.referencia, fila.benchmark)
            self.assertEqual(fila.benchmark, self.serie.loc[year, "benchmark"])
            self.assertTrue(datos_anuales.loc[datos_anuales.referencia, "NPRESTDOMIC"].eq(fila.referencia).all())
        ajuste = config["indicadores"]["NPRESTDOMIC"]
        panel = self.serie.copy()
        panel[["referencia", "bus_lider"]] = calculado[["referencia", "bus_lider"]]
        fig = grafico(panel, 2025, ajuste["titulo"], ajuste["subtitulo"], "Préstamos",
                      "Media móvil de 3 años", True)
        banda, = fig.axes[0].collections
        vertices = {tuple(p) for p in banda.get_paths()[0].vertices}
        for year, fila in calculado.iterrows():
            self.assertEqual({y for x, y in vertices if x == year}, {fila.referencia, fila.benchmark})

    def test_prevision_metas_y_validacion(self):
        futuro = self.serie.loc[2026:2028]
        self.assertTrue(futuro[["bus", "benchmark", "referencia"]].isna().all().all())
        self.assertTrue(self.serie.loc[:2025, "prevision"].isna().all())
        config = self.config["indicadores"]["NPRESTDOMIC"]
        for col, clave in [("meta", "metas"), ("limite", "limites")]:
            self.assertEqual(self.serie[col].to_dict(), {int(y): v for y, v in config[clave].items() if int(y) <= 2028})
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
            self.assertGreater(linea.get_zorder(), barras[0].patches[0].get_zorder())
            self.assertEqual((linea.get_marker(), linea.get_markerfacecolor(), linea.get_markeredgecolor()),
                             ("o", "white", color))
            muestra = next(h for h in fig.legends[0].legend_handles if h.get_label() == linea.get_label())
            for atributo in ("linestyle", "marker", "markersize", "markerfacecolor", "markeredgecolor"):
                lector = f"get_{atributo}"
                self.assertEqual(getattr(muestra, lector)(), getattr(linea, lector)())
        self.assertTrue(ax.lines[0].is_dashed())
        self.assertFalse(ax.lines[1].is_dashed())
        banda, = ax.collections
        self.assertEqual(tuple(banda.get_facecolor()[0]), to_rgba(AZUL, ALFA_BANDA))
        self.assertLess(ax.yaxis.get_zorder(), banda.get_zorder())
        self.assertLess(banda.get_zorder(), barras[0].patches[0].get_zorder())
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
            self.assertGreater(etiqueta.get_zorder(), ax.lines[0].get_zorder())
            self.assertEqual(etiqueta.get_rotation(), 90)
            self.assertEqual(etiqueta.get_text(), numero(rect.get_height()))
            caja = etiqueta.get_window_extent(renderer)
            barra = rect.get_window_extent(renderer)
            self.assertTrue(barra.contains(caja.x0, caja.y0))
            self.assertTrue(barra.contains(caja.x1, caja.y1))

    def test_indicadores_ampliados(self):
        pruebas = [
            ("NMONPAGOLIC", "NMONPAGOLIC", None, 1, max, "Regresión lineal"),
            ("USUARIOS_POR_PUESTO", "NUSUARIOPROP", "NPUESTOSLECT", 1, min, "Media móvil de 3 años"),
            ("PCT_GASTO_ELECTRONICO", "GASTOINFOELECT", "GASTORECINFO", 100, max,
             "Suavizado exponencial simple"),
        ]
        for codigo, numerador, denominador, factor, mejor, modelo in pruebas:
            with self.subTest(codigo=codigo):
                carpeta = self.distribucion.parent / codigo
                serie = pd.read_csv(carpeta / "serie.csv", index_col="Anio", sep=";", decimal=",")
                ranking = pd.read_csv(carpeta / "seleccion.csv", sep=";", decimal=",")
                self.assertEqual(ranking.modelo.iloc[0], modelo)
                self.assertTrue(serie.loc[2026:, "prevision"].notna().all())
                self.assertTrue(serie.loc[2026:, ["benchmark", "referencia"]].isna().all().all())

                def dato(year, centro):
                    valor = self.original.get((year, centro, numerador))
                    if denominador:
                        divisor = self.original.get((year, centro, denominador), 0)
                        return factor * (valor / divisor) if valor is not None and divisor > 0 else None
                    return valor

                for year, fila in serie.loc[:2025].iterrows():
                    casos = [dato(year, centro) for centro in self.presenciales - {"67"}
                             if self.original.get((year, centro, "NUSUARIOPROP"), 0) > 40000]
                    casos = [v for v in casos if v is not None and (factor != 100 or 0 <= v <= 100)]
                    self.assertAlmostEqual(fila.bus, dato(year, "67"))
                    self.assertAlmostEqual(fila.referencia, mejor([fila.bus, *casos]))
                    self.assertEqual(fila.bus_lider, factor != 100 and fila.bus == fila.referencia)
                    self.assertAlmostEqual(fila.benchmark, statistics.median(casos))
                    self.assertEqual(fila.con_dato, len(casos))
                if mejor is min:
                    self.assertTrue(serie.meta.lt(serie.limite).all())
                    self.assertTrue(serie.loc[:2025, "referencia"].le(serie.loc[:2025, "benchmark"]).all())
                if factor == 100:
                    for col in ["bus", "benchmark", "referencia", "prevision", "limite", "meta"]:
                        self.assertTrue(serie[col].dropna().between(0, 100).all())
                historico = serie.loc[:2025]
                if codigo == "NMONPAGOLIC":
                    lideres = historico.loc[historico.bus_lider.eq(True)]
                    self.assertEqual(lideres.index.tolist(), list(range(2020, 2026)))
                    self.assertEqual(list(lideres.bus), list(lideres.referencia))
                    ajuste = self.config["indicadores"][codigo]
                    fig = grafico(serie, 2025, ajuste["titulo"], ajuste["subtitulo"], ajuste["unidad"],
                                  modelo, True)
                    marcador = next(linea for linea in fig.axes[0].lines
                                    if linea.get_gid() == "serie-reference-liderazgo")
                    self.assertEqual(list(marcador.get_xdata()), list(lideres.index))
                    self.assertEqual(list(marcador.get_ydata()), list(lideres.bus))
                    self.assertEqual(marcador.get_markerfacecolor(), BUS)
                    self.assertEqual(marcador.get_markeredgecolor(), REFERENCIA)
                svg = (carpeta / "grafica.svg").read_text()
                self.assertEqual('id="serie-reference-liderazgo"' in svg, codigo == "NMONPAGOLIC")
                self.assertIn("excluida la BUS", svg)
                self.assertIn("incluida la BUS", svg)
                if factor == 100:
                    self.assertIn("máximo descriptivo anual", svg)
                with Image.open(carpeta / "grafica.png") as imagen:
                    self.assertEqual(imagen.size, (3200, 1480))
                html = (carpeta / "index.html").read_text()
                self.assertIn(f'<option value="../{codigo}/" selected>', html)
                self.assertEqual(html.count("<svg "), 1)

    def test_formula_sin_denominador_valido(self):
        config = deepcopy(self.config)
        config["inicio"] = config["fin"] = 2025
        codigo = "USUARIOS_POR_PUESTO"
        datos = pd.DataFrame([
            (2025, "67", "NUSUARIOPROP", 50000), (2025, "67", "NPUESTOSLECT", 5000),
            (2025, "01", "NUSUARIOPROP", 45000), (2025, "01", "NPUESTOSLECT", 0),
            (2025, "02", "NUSUARIOPROP", 46000),
            (2025, "03", "NUSUARIOPROP", 48000), (2025, "03", "NPUESTOSLECT", 4800),
        ], columns=["Anio", ID, "Codigo_Tecnico", "Valor"])
        centros = pd.DataFrame([(centro, centro, "Presencial") for centro in ["67", "01", "02", "03"]],
                               columns=[ID, "Biblioteca", "Modalidad"])
        serie, miembros = preparar(datos, centros, config, codigo)
        self.assertEqual(serie.loc[2025, "elegibles"], 3)
        self.assertEqual(serie.loc[2025, "con_dato"], 1)
        self.assertEqual(serie.loc[2025, "benchmark"], 10)
        self.assertEqual(serie.loc[2025, "referencia"], 10)
        self.assertTrue(serie.loc[2025, "bus_lider"])
        self.assertTrue(miembros.set_index(ID).loc["03", "referencia"])
        self.assertTrue(miembros.set_index(ID).loc[["01", "02"], codigo].isna().all())

    def test_horizontes_e_intervalos(self):
        for codigo, ajuste in self.config["indicadores"].items():
            with self.subTest(codigo=codigo):
                carpeta = self.distribucion.parent / codigo
                corto = pd.read_csv(carpeta / "serie.csv", index_col="Anio", sep=";", decimal=",")
                largo = pd.read_csv(carpeta / "serie-5.csv", index_col="Anio", sep=";", decimal=",")
                pd.testing.assert_frame_equal(corto, largo.loc[:2028])
                futuro = largo.loc[2026:]
                self.assertEqual(list(futuro.index), list(range(2026, 2031)))
                li, ls = futuro.prediccion_inferior_95, futuro.prediccion_superior_95
                minimo, maximo = ajuste["limites_naturales"]
                if codigo == "NPRESTDOMIC":
                    self.assertTrue(li.isna().all() and ls.isna().all())
                else:
                    self.assertTrue((li <= futuro.prevision).all() and (futuro.prevision <= ls).all())
                    self.assertTrue(li.ge(minimo).all())
                    if maximo is not None:
                        self.assertTrue(ls.le(maximo).all())
                self.assertTrue(largo.loc[:2025, ["prediccion_inferior_95", "prediccion_superior_95"]]
                                .isna().all().all())
                for col, clave in [("meta", "metas"), ("limite", "limites")]:
                    self.assertEqual(largo[col].to_dict(), {int(y): v for y, v in ajuste[clave].items()})
                detalle = pd.read_csv(carpeta / "validacion-intervalos.csv", sep=";", decimal=",")
                resumen = pd.read_csv(carpeta / "cobertura-intervalos.csv", index_col="horizonte",
                                     sep=";", decimal=",")
                for h, casos in detalle.groupby("horizonte"):
                    validos = casos.dropna(subset=["inferior", "superior"])
                    self.assertEqual(len(validos), resumen.loc[h, "estimables"])
                    self.assertEqual(len(casos), 1 if codigo == "NPRESTDOMIC" else 6 - h)
                    self.assertEqual(int(validos.observado.between(validos.inferior, validos.superior).sum()),
                                     resumen.loc[h, "cubiertos"])
                    self.assertTrue(all(real == largo.loc[origen + h, "bus"]
                                        for origen, real in zip(casos.origen, casos.observado)))
                self.assertIn('data-horizonte="3"', (carpeta / "index.html").read_text())
                self.assertIn('data-horizonte="5"', (carpeta / "5.html").read_text())
                svg = (carpeta / "grafica-5.svg").read_text()
                self.assertIn('id="serie-bus_forecast-punto"', svg)
                if codigo == "NPRESTDOMIC":
                    self.assertNotIn('id="serie-prediction_interval-2030"', svg)
                    self.assertIn("Sin intervalo del 95 % defendible", svg)
                    self.assertIn("2022–2025 (n=4)", svg)
                else:
                    self.assertIn('id="serie-prediction_interval-2030"', svg)
                    self.assertIn("95 % nominal", svg)
                    self.assertIn("2016–2025 (n=10)", svg)

    def test_revision_predictiva(self):
        carpeta = self.distribucion
        leer = lambda ruta: pd.read_csv(ruta, sep=";", decimal=",")
        ajuste = leer(carpeta / "ajuste-publicado.csv").iloc[0]
        self.assertEqual((ajuste.inicio, ajuste.fin, ajuste.n_ajuste), (2022, 2025, 4))
        detalle = leer(carpeta / "revision-errores.csv")
        reciente = detalle.loc[detalle.escenario.eq("Reciente")]
        self.assertTrue((reciente.n_ajuste == reciente.origen - 2022 + 1).all())
        comun = leer(carpeta / "revision-metricas.csv").query("comparacion == 'origen_comun_reciente'")
        self.assertEqual(set(comun.escenario), {"Completa", "Reciente", "Cambio de nivel", "Transformada"})
        self.assertTrue(comun.n.eq(1).all() and comun.horizonte.eq(1).all())
        futuros = leer(carpeta / "revision-escenarios.csv")
        paso = futuros.query("escenario == 'Cambio de nivel'")
        np.testing.assert_allclose(paso.previsto, self.serie.loc[2020:2025, "bus"].mean())
        gasto = leer(carpeta.parent / "PCT_GASTO_ELECTRONICO" / "ajuste-publicado.csv").iloc[0]
        self.assertEqual((gasto.modelo, gasto.transformacion), ("Ingenuo", "logit"))

    def test_intervalo_lineal_para_nueva_observacion(self):
        y = np.array([14., 12., 16., 17., 18., 21., 22.])
        x = sm.add_constant(np.arange(len(y)))
        futuro = sm.add_constant(np.arange(len(y), len(y) + 3))
        esperado = sm.OLS(y, x).fit().get_prediction(futuro).summary_frame(alpha=.05)
        calculado = intervalo("Regresión lineal", y, 3, (None, None))
        np.testing.assert_allclose(calculado, esperado[["obs_ci_lower", "obs_ci_upper"]])
        self.assertTrue(np.isnan(intervalo("Media móvil de 3 años", y[:5], 3, (0, None))).all())

    def test_archivos_estaticos(self):
        html = (self.distribucion / "index.html").read_text(encoding="utf-8")
        self.assertIn("<h1>Indicadores EFQM 2028</h1>", html)
        self.assertIn('<svg ', html)
        self.assertEqual(html.count('<fieldset>'), 3)
        for opciones in CONTROLES.values():
            for serie, nombre in opciones.items():
                self.assertIn(f'name="{serie}" checked> {nombre}', html)
                self.assertIn(f'data-etiqueta="{serie}" aria-label="Cifras de {nombre}"', html)
        self.assertIn("Descargar imagen PNG", html)
        self.assertIn("Restablecer selección", html)
        for accesorio in ["<table", "<details", "<article"]:
            self.assertNotIn(accesorio, html)
        with Image.open(self.distribucion / "grafica.png") as png:
            self.assertEqual(png.size, (3200, 1480))
        svg = (self.distribucion / "grafica.svg").read_text(encoding="utf-8")
        self.assertIn('id="etiqueta-target_future-2026" style="display:none"', svg)
        self.assertIn('id="etiqueta-bus_forecast-2026">', svg)
        self.assertIn("stroke-dasharray", svg)
        for contenido in [
            "Préstamos domiciliarios de material bibliográfico", "más de 40.000",
            "REBIUN Data Explorer", "mediana del grupo", "mejor resultado anual", "intervalo de confianza estadístico",
            "Metas y límites ilustrativos", "media móvil de 3 años", "incertidumbre",
            "350.602", "365.118", "354.793",
        ]:
            self.assertIn(contenido, svg)
