// Variables
let report = "";

let x = 10;
const y = 20;

if (x + y == 30) {
    report = report + "variables OK | ";
}


// Funciones

function sum(a, b) {
    return a + b;
}

if (sum(5, 7) == 12) {
    report = report + "funciones OK | ";
}


// Recursion
function factorial(n) {
    if (n <= 1) {
        return 1;
    }

    return n * factorial(n - 1);
}

if (factorial(5) == 120) {
    report = report + "recursion OK | ";
}


// Clousures y hoisting de funcion

let counter = makeCounter(10);

let a = counter();
let b = counter();
let c = counter();

if (a == 11 && b == 12 && c == 13) {
    report = report + "clousures OK | ";
}

let add5 = outer(5);

if (add5(10) == 15) {
    report = report + "clousure anidado OK | ";
}

function makeCounter(start) {
    let count = start;

    function inc() {
        count = count + 1;
        return count;
    }

    return inc;
}

function outer(a) {
    function inner(b) {
        return a + b;
    }

    return inner;
}


// Scopes

{
    let x = 100;

    {
        let x = 200;

        if (x == 200) {
            report = report + "scope anidado OK | ";
        }
    }

    if (x == 100) {
        report = report + "block scope OK | ";
    }
}

if (x == 10) {
    report = report + "scope global OK | ";
}


// Booleanos

if (true && !false) {
    report = report + "booleanos OK | ";
}


// While

let i = 0;

while (i < 3) {
    i = i + 1;
}

if (i == 3) {
    report = report + "while OK | ";
}



// Expresiones

if ((2 + 3) * (4 + 1) == 25) {
    report = report + "expresiones OK";
}
report;