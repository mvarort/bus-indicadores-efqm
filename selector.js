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

function actualizar() {
    const visible = Object.fromEntries(casillas.map(({name, checked}) => [name, checked]));
    Object.entries(series).forEach(([id, nodos]) => {
        nodos.forEach(nodo => ocultar(nodo, !visible[id]));
    });

    cifras.forEach(casilla => {
        const id = casilla.dataset.etiqueta;
        etiquetas[id].forEach(nodo => ocultar(nodo, !visible[id] || !casilla.checked));
    });

    for (const grupo of geometria.grupos) {
        const elegidas = grupo.filter(({id}) => visible[id]);
        const ancho = elegidas.reduce((suma, barra) => suma + barra.ancho, 0)
            + geometria.separacion * Math.max(0, elegidas.length - 1);
        let izquierda = -ancho / 2;
        for (const barra of elegidas) {
            const centro = izquierda + barra.ancho / 2;
            const ajuste = (centro - barra.origen) * geometria.escala;
            [...series[barra.id], ...etiquetas[barra.id]].forEach(nodo => mover(nodo, ajuste));
            izquierda += barra.ancho + geometria.separacion;
        }
    }

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
        "nota-plan": Object.values(combinaciones).flat().some(id => visible[id]),
        "nota-prevision": visible.bus_forecast,
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
    const copia = grafica.cloneNode(true);
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
        enlace.download = `${location.pathname.split("/").filter(Boolean).pop() || "indicador"}-EFQM.png`;
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
if (vista && vista.length === controles.length && /^[01]+$/.test(vista)) {
    controles.forEach((control, i) => { control.checked = vista[i] === "1"; });
}
document.querySelector("#indicador").addEventListener("change", ({target}) => {
    const destino = new URL(target.value, location.href);
    destino.searchParams.set("vista", controles.map(control => Number(control.checked)).join(""));
    location.assign(destino);
});

panel.addEventListener("change", actualizar);
document.querySelector("#restablecer").addEventListener("click", () => {
    [...casillas, ...cifras].forEach(casilla => { casilla.checked = casilla.defaultChecked; });
    actualizar();
});
document.querySelector("#descargar").addEventListener("click", descargar);
actualizar();
