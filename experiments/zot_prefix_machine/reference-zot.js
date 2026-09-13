/**
 *    Zot
 *    https://web.archive.org/web/20200414141014/http://www.nyu.edu/projects/barker/Iota/zot.html
 *    originally by Chris Barker
 *    modified by Mingli Yuan
 *
**/

import { loadFile } from "std";


let output;

function I(x) { return x; }

function K(x) {
    function K1(y) {
        return(x);
    }
    return K1;
}

function S(x) {
    function S1(y) {
        function S2(z) {
            return ((x (z))(y (z)));
        }
        return S2;
    }
    return S1;
}

function zero(c) {
    function basis(f) {
        return ((f(S))(K));
    }
    return (c(basis));
}

function one(c) {
    function bigleft (L) {
        function left (l) {
            function bigright (R) {
                function right (r) {
                    return (c(l(r)));
                }
                return (R(right));
            }
            return bigright;
        }
        return (L(left));
    }
    return bigleft;
}

function trivial(x) {
    return x(I);
}

function zot(prog) {
    function process(position, value) {
        if (position >= prog.length) { return value }
        if (prog.charAt(position) === "0") {
            return process (position + 1, value(zero))
        }
        return process (position + 1, value(one))
    }
    return process(0, trivial);
}

function interrogate (f) {
    return ((((f(I))(I))(I))(K));
}

function pr(ch) {
    output.push(((interrogate(ch))("0"))("1"));
    return pr;
}

function run(prog) {
    output = [];
    ((zot(prog))(K(K(K(K(K(K(I))))))))(pr);
    return output.join('');
}

const progFile = scriptArgs[1], data = scriptArgs[2];
console.log(run(loadFile(progFile).trim() + data.trim()));
