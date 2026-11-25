"use strict";

const assert = require("node:assert/strict");
const {test} = require("node:test");
const colocar = require("./colocacion.js");

const limites = {x:0,y:0,w:200,h:200};
const texto = {w:9,h:24};
const margen = 2;

test("sitúa las cifras de barras nulas o muy bajas en el exterior", () => {
    for (const h of [0, 2]) {
        const barra = {x:60,y:200-h,w:15,h};
        const [lugar] = colocar({etiquetas:[{barra,texto}],segmentos:[],limites,margen,barras:[barra]});
        assert(lugar.exterior && lugar.y+lugar.h < barra.y);
    }
});

test("desplaza las cifras de una barra alta si hay referencias en su extremo superior", () => {
    const barra = {x:50,y:1,w:24,h:199};
    const segmentos = [[0,4,200,6,1], [62,1,62,1,3], [0,16,200,15,1]];
    const [lugar] = colocar({etiquetas:[{barra,texto}],segmentos,limites,margen,barras:[barra]});
    assert(!lugar.exterior && lugar.y > 18);
});

test("evita un intervalo vertical amplio, sus remates y una segunda cifra", () => {
    const barra = {x:40,y:95,w:32,h:105};
    const segmentos = [[56,5,56,195,.5], [50,5,62,5,.5], [50,195,62,195,.5], [56,95,56,95,3]];
    const [a,b] = colocar({etiquetas:[{barra,texto},{barra,texto}],segmentos,limites,margen,barras:[barra]});
    for (const lugar of [a,b]) {
        assert(!lugar.exterior);
        assert(lugar.x+lugar.w <= 54 || lugar.x >= 58);
    }
    assert(a.x+a.w <= b.x || b.x+b.w <= a.x || a.y+a.h <= b.y || b.y+b.h <= a.y);
});
