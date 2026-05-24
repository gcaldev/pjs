function fib(n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}
const n = 20;

const start = performance.now();

const result = fib(n);

const end = performance.now();

console.log(`fib(${n}) = ${result}`);
console.log(`time = ${(end - start).toFixed(2)} ms`);