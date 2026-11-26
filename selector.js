"use strict";

const panel = document.querySelector("#opciones");
const grafica = document.querySelector("#grafica svg");
const geometria = JSON.parse(document.querySelector("#geometria").textContent);
const casillas = [...panel.querySelectorAll('input[name]')];
const cifras = [...panel.querySelectorAll('[data-etiqueta]')];
const etiquetas = Object.fromEntries(cifras.map(({dataset}) => [
    dataset.etiqueta, [...grafica.querySelectorAll(`[id^="etiqueta-${dataset.etiqueta}-"]`)],
]));
const series = Object.fromEntries(casillas.map(({name}) => [
    name, [...grafica.querySelectorAll(`[id^="serie-${name}-"]`)],
]));
const combinaciones = {
    threshold: ["threshold_historical", "threshold_future"],
    target: ["target_historical", "target_future"],
};
const leyenda = [...grafica.querySelectorAll('[id^="leyenda-"][id$="-texto"]')].map(texto => {
    const nombre = texto.id.slice("leyenda-".length, -"-texto".length);
    const muestra = grafica.querySelector(`#leyenda-${nombre}-muestra`);
    const boceto = muestra.querySelector("path");
    return {
        texto, muestra, boceto, estilo: boceto.getAttribute("style"),
        fuentes: combinaciones[nombre] || [nombre],
        inicio: muestra.getBBox().x,
    };
});
const notas = [...grafica.querySelectorAll('[id^="nota-"]')].map(nodo => ({
    nodo, y: nodo.getBBox().y,
}));

function ocultar(nodo, invisible) {
    nodo.style.display = invisible ? "none" : "";
}

function mover(nodo, x, y = 0) {
    if (Math.abs(x) < 1e-8 && Math.abs(y) < 1e-8) {
        nodo.removeAttribute("transform");
    } else {
        nodo.setAttribute("transform", `translate(${x} ${y})`);
    }
}

const barrasRotuladas = geometria.grupos.flat().flatMap(({id, color}) =>
    etiquetas[id].map(nodo => {
        const year = nodo.id.split("-").at(-1);
        const glifos = nodo.querySelector(":scope > g[transform]");
        nodo.querySelector(':scope > g[id^="patch_"]')?.remove();
        return {id, year, color, nodo, glifos, barra: grafica.querySelector(`#serie-${id}-barra-${year}`)};
    })
).sort((a,b) => Number(b.id.startsWith("bus_")) - Number(a.id.startsWith("bus_")));

function situarRotulos(visible, ajustes, escalaPantalla) {
    const rotulos = barrasRotuladas.filter(({nodo}) => nodo.style.display !== "none");
    const margen = Math.max(1.45, 1.8/escalaPantalla);
    const segmentos = Object.entries(geometria.segmentos).flatMap(([id, trazos]) =>
        visible[id] ? trazos.map(([x1,y1,x2,y2,r]) => {
            const dx = ajustes[id] || 0;
            return [x1+dx, y1, x2+dx, y2, r];
        }) : []);
    const medida = ({x,y,width,height}) => ({x,y,w:width,h:height});
    const medidaBarra = ({barra, id}) => {
        const caja = medida(barra.getBBox());
        caja.x += ajustes[id] || 0;
        return caja;
    };
    const barras = barrasRotuladas.filter(({id}) => visible[id]).map(medidaBarra);
    const entradas = rotulos.map(({nodo, barra, id}) => {
        nodo.querySelector(".fondo-etiqueta")?.remove();
        return {barra: medidaBarra({barra, id}), texto: medida(nodo.getBBox())};
    });
    const salida = colocarEtiquetas({etiquetas:entradas, segmentos, limites:geometria.limites, margen, barras});
    rotulos.forEach(({nodo, glifos, id, color}, i) => {
        const {texto} = entradas[i];
        const lugar = salida[i];
        if (!lugar) {
            mover(nodo, ajustes[id] || 0);
            return;
        }
        mover(nodo, lugar.x - texto.x, lugar.y - texto.y);
        const dentroHistorico = !lugar.exterior && (id.endsWith("_historical") || id === "bus_actual");
        const exterior = color === "#388E3C" ? "#216528" : color === "#C8102E" ? "#9B1025" : color;
        glifos.style.fill = dentroHistorico ? "white" : lugar.exterior ? exterior : color;
        if (lugar.exterior || id === "bus_forecast") {
            const fondo = document.createElementNS(grafica.namespaceURI, "rect");
            fondo.setAttribute("class", "fondo-etiqueta");
            fondo.setAttribute("fill", lugar.exterior ? "#ffffff" : "#fbe7ea");
            fondo.setAttribute("x", texto.x - 1);
            fondo.setAttribute("y", texto.y - 1);
            fondo.setAttribute("width", texto.w + 2);
            fondo.setAttribute("height", texto.h + 2);
            nodo.prepend(fondo);
        }
    });
}

function actualizar(escalaPantalla = grafica.getScreenCTM().a) {
    const visible = Object.fromEntries(casillas.map(control => [control.name, control.checked && !control.disabled && !control.closest("[hidden]")]));
    Object.entries(series).forEach(([id, nodos]) => {
        nodos.forEach(nodo => ocultar(nodo, !visible[id]));
    });

    cifras.forEach(casilla => {
        const id = casilla.dataset.etiqueta;
        etiquetas[id].forEach(nodo => ocultar(nodo, !visible[id] || !casilla.checked));
    });

    const ajustes = {};
    let ajusteIntervalo = 0;
    for (const grupo of geometria.grupos) {
        const elegidas = grupo.filter(({id}) => visible[id]);
        const ancho = elegidas.reduce((suma, barra) => suma + barra.ancho, 0)
            + geometria.separacion * Math.max(0, elegidas.length - 1);
        let izquierda = -ancho / 2;
        for (const barra of elegidas) {
            const centro = izquierda + barra.ancho / 2;
            const ajuste = (centro - barra.origen) * geometria.escala;
            ajustes[barra.id] = ajuste;
            series[barra.id].forEach(nodo => mover(nodo, ajuste));
            if (barra.id === "bus_forecast") ajusteIntervalo = ajuste;
            izquierda += barra.ancho + geometria.separacion;
        }
    }

    ajustes.prediction_interval = ajusteIntervalo;
    series.prediction_interval.forEach(nodo => mover(nodo, ajusteIntervalo));
    grafica.querySelectorAll('[id^="etiqueta-prediction_interval-"]').forEach(
        nodo => ocultar(nodo, !visible.prediction_interval),
    );
    situarRotulos(visible, ajustes, escalaPantalla);

    let hueco = 0;
    leyenda.forEach((elemento, i) => {
        const {texto, muestra, boceto, estilo, fuentes, inicio} = elemento;
        const activa = fuentes.some(id => visible[id]);
        [texto, muestra].forEach(nodo => {
            ocultar(nodo, !activa);
            mover(nodo, -hueco);
        });
        boceto.setAttribute("style", estilo);
        if (fuentes.length === 2 && !visible[fuentes[0]] && visible[fuentes[1]]) {
            boceto.style.stroke = boceto.style.fill;
            boceto.style.strokeWidth = "1.1";
            boceto.style.fill = "none";
        }
        if (!activa && i + 1 < leyenda.length) {
            hueco += leyenda[i + 1].inicio - inicio;
        }
    });

    const mostrarNotas = {
        "nota-fuente": true,
        "nota-comparacion": visible.benchmark || visible.reference || visible.comparison_band,
        "nota-banda": visible.comparison_band,
        "nota-liderazgo": visible.reference,
        "nota-plan": Object.values(combinaciones).flat().some(id => visible[id]),
        "nota-prevision": visible.bus_forecast || visible.prediction_interval,
        "nota-intervalo": visible.prediction_interval,
    };
    let siguiente = 0;
    for (const {nodo, y} of notas) {
        const activa = mostrarNotas[nodo.id] ?? true;
        ocultar(nodo, !activa);
        if (activa) {
            mover(nodo, 0, notas[siguiente].y - y);
            siguiente++;
        }
    }
}

async function descargar() {
    const estado = document.querySelector("#estado");
    actualizar(3200 / grafica.viewBox.baseVal.width);
    const copia = grafica.cloneNode(true);
    actualizar();
    copia.querySelector("metadata")?.remove();
    const xml = new XMLSerializer().serializeToString(copia);
    const url = URL.createObjectURL(new Blob([xml], {type: "image/svg+xml;charset=utf-8"}));
    try {
        const imagen = new Image();
        imagen.src = url;
        await imagen.decode();
        const lienzo = document.createElement("canvas");
        lienzo.width = 3200;
        lienzo.height = 1480;
        lienzo.getContext("2d").drawImage(imagen, 0, 0, lienzo.width, lienzo.height);
        const png = await new Promise(resolve => lienzo.toBlob(resolve, "image/png"));
        if (!png) throw new Error("PNG vacío");
        const enlace = document.createElement("a");
        enlace.href = URL.createObjectURL(png);
        const {codigo, horizonte} = document.querySelector("main").dataset;
        const periodo = inicial.value === limites.inicioDisponible && final.value === limites.finDisponible
            ? "" : `-${inicial.value}-${final.value}`;
        enlace.download = `${codigo}-EFQM${periodo}${horizonte === "0" ? "" : `-${horizonte}a`}.png`;
        enlace.click();
        setTimeout(() => URL.revokeObjectURL(enlace.href), 1000);
        estado.textContent = "";
    } catch (error) {
        estado.textContent = "No se pudo generar el PNG.";
    } finally {
        URL.revokeObjectURL(url);
    }
}

const controles = [...casillas, ...cifras];
const vista = new URLSearchParams(location.search).get("vista");
if (vista && /^[01]+$/.test(vista)) {
    const restaurada = vista.length === controles.length - 1 ? vista.slice(0, 9) + "1" + vista.slice(9) : vista;
    if (restaurada.length === controles.length) {
        controles.forEach((control, i) => { control.checked = restaurada[i] === "1"; });
    }
}
const indicador = document.querySelector("#indicador");
const prospectiva = document.querySelector("#horizonte");
const inicial = document.querySelector("#anio-inicial");
const final = document.querySelector("#anio-final");
const limites = document.querySelector("main").dataset;
const horizonteAnterior = new URLSearchParams(location.search).get("prospectiva");
if (prospectiva.hidden && [...prospectiva.options].some(opcion => opcion.value === horizonteAnterior)) {
    prospectiva.value = horizonteAnterior;
}

function cambiarVista() {
    if (Number(inicial.value) > Number(final.value)) return;
    const horizonte = prospectiva.value;
    const conProspectiva = final.value === limites.finDisponible;
    const completo = conProspectiva && inicial.value === limites.inicioDisponible;
    const alternativo = horizonte !== limites.horizonteInicial;
    const archivo = completo ? (alternativo ? `${horizonte}.html` : "") :
        `historico-${inicial.value}-${final.value}${conProspectiva && alternativo ? `-${horizonte}` : ""}.html`;
    const destino = new URL(indicador.value + archivo, location.href);
    if (!conProspectiva) destino.searchParams.set("prospectiva", horizonte);
    destino.searchParams.set("vista", controles.map(control => Number(control.checked)).join(""));
    location.assign(destino);
}
[indicador, prospectiva, inicial, final].forEach(control => control.addEventListener("change", cambiarVista));

panel.addEventListener("change", () => actualizar());
const redimensionar = new ResizeObserver(() => actualizar());
redimensionar.observe(grafica);
document.querySelector("#restablecer").addEventListener("click", () => {
    [...casillas, ...cifras].forEach(casilla => { casilla.checked = casilla.defaultChecked; });
    actualizar();
});
document.querySelector("#descargar").addEventListener("click", descargar);
actualizar();
