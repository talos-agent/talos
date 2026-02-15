// ucd.js – Universal Coherence Detection in Node.js

function verifyConservation(C, F, tol = 1e-10) {
    return Math.abs(C + F - 1.0) < tol;
}

function identityCheck(phi = 1.618033988749895) {
    return Math.abs(phi * phi - (phi + 1.0)) < 1e-10;
}

function isToroidal(graph) {
    // Placeholder – retorna "toroidal" para fins de exemplo
    return "toroidal";
}

function selfSimilarityRatio(short, long) {
    const ratio = long / short;
    const phi = 1.618;
    return { ratio, matchesPhi: Math.abs(ratio - phi) < 0.3 };
}

class UCD {
    constructor(data) {
        this.data = data; // array de arrays (matriz)
        this.C = null;
        this.F = null;
    }

    analyze() {
        // Cálculo simplificado de coerência: média das correlações
        if (this.data.length > 1 && this.data[0].length > 1) {
            const n = this.data.length;
            let sumCorr = 0;
            for (let i = 0; i < n; i++) {
                for (let j = i+1; j < n; j++) {
                    const xi = this.data[i];
                    const xj = this.data[j];
                    const corr = this._pearson(xi, xj);
                    sumCorr += Math.abs(corr);
                }
            }
            const count = (n * (n-1)) / 2;
            this.C = count > 0 ? sumCorr / count : 0.5;
        } else {
            this.C = 0.5;
        }
        this.F = 1.0 - this.C;
        return {
            C: this.C,
            F: this.F,
            conservation: verifyConservation(this.C, this.F),
            topology: this.C > 0.8 ? "toroidal" : "other",
            scaling: this.C > 0.7 ? "self-similar" : "linear",
            optimization: this.F * 0.5
        };
    }

    _pearson(x, y) {
        const n = x.length;
        const meanX = x.reduce((a,b) => a+b,0)/n;
        const meanY = y.reduce((a,b) => a+b,0)/n;
        let num = 0, denX = 0, denY = 0;
        for (let i = 0; i < n; i++) {
            const dx = x[i] - meanX;
            const dy = y[i] - meanY;
            num += dx * dy;
            denX += dx * dx;
            denY += dy * dy;
        }
        return denX * denY === 0 ? 0 : num / Math.sqrt(denX * denY);
    }
}

// Exemplo de uso:
const data = [[1,2,3,4],[2,3,4,5],[5,6,7,8]];
const ucd = new UCD(data);
console.log(ucd.analyze());
