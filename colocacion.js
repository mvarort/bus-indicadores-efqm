"use strict";

// Cajas y segmentos en un mismo sistema de coordenadas de pantalla.
function colocarEtiquetas({etiquetas, segmentos, limites, margen, barras = []}) {
    const ocupadas = [];
    const interseca = (a, b) => a.x < b.x + b.w && a.x + a.w > b.x
        && a.y < b.y + b.h && a.y + a.h > b.y;
    const ampliar = (c, p) => ({x:c.x-p, y:c.y-p, w:c.w+2*p, h:c.h+2*p});
    const dentro = (a, b) => a.x >= b.x && a.y >= b.y
        && a.x + a.w <= b.x + b.w && a.y + a.h <= b.y + b.h;
    const toca = (c, [x1,y1,x2,y2,radio]) => {
        const caja = ampliar(c, radio);
        const izquierda = Math.max(caja.x, Math.min(x1,x2));
        const derecha = Math.min(caja.x+caja.w, Math.max(x1,x2));
        if (izquierda > derecha) return false;
        const altura = x => y1 + (y2-y1)*(x-x1)/(x2-x1);
        const [a,b] = x1 === x2 ? [y1,y2] : [altura(izquierda),altura(derecha)];
        return Math.min(a,b) <= caja.y+caja.h && Math.max(a,b) >= caja.y;
    };

    return etiquetas.map(({barra, texto}) => {
        const {w,h} = texto;
        const centro = barra.x + barra.w/2;
        const paso = Math.max(margen, 1);
        const seguro = c => dentro(c, limites) && !ocupadas.some(b=>interseca(ampliar(c,margen),b))
            && !segmentos.some(s=>toca(ampliar(c,margen),s));
        const ejes = [centro-w/2, barra.x+margen, barra.x+barra.w-w-margen];
        for (let y = barra.y+margen; y+h <= barra.y+barra.h-margen; y += paso) {
            for (const x of ejes) {
                const caja = {x,y,w,h};
                if (dentro(ampliar(caja,margen),barra) && seguro(caja)) {
                    ocupadas.push(caja);
                    return {...caja, exterior:false};
                }
            }
        }

        const libre = caja => seguro(caja) && !barras.some(b=>interseca(ampliar(caja,margen),b));
        const opciones = [centro-w/2, barra.x-w-2*margen, barra.x+barra.w+2*margen];
        for (let d = 0; d <= limites.h; d += paso) {
            const alturas = [barra.y-h-2*margen-d, barra.y+2*margen+d];
            for (const y of alturas) {
                for (const x of opciones) {
                    const caja = {x,y,w,h};
                    if (!interseca(ampliar(caja,margen),barra) && libre(caja)) {
                        ocupadas.push(ampliar(caja,margen));
                        return {...caja, exterior:true};
                    }
                }
            }
        }
        // Último recurso en la zona de dibujo, para barras pegadas al eje.
        for (let y = limites.y; y+h <= limites.y+limites.h; y += paso) {
            for (const x of opciones) {
                const caja = {x,y,w,h};
                if (libre(caja)) {
                    ocupadas.push(ampliar(caja,margen));
                    return {...caja, exterior:true};
                }
            }
        }
        return null;
    });
}

if (typeof module !== "undefined") {
    module.exports = colocarEtiquetas;
    if (require.main === module) {
        const entrada = JSON.parse(require("node:fs").readFileSync(0, "utf8"));
        process.stdout.write(JSON.stringify(colocarEtiquetas(entrada)));
    }
}
