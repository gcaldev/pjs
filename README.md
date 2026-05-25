# PJS

Implementación en Python de un subset de Javascript.

Se recomienda el uso de [Black](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) para formateo de código.

```sh
black .
```

## Ejecución

- **Ejecutar interprete simple:**

```sh
python main.py
```

- **Ejecutar interprete multilínea:**

```sh
python main.py --multiline
```

- **Ejecutar tests:**

```sh
python -m pytest -q
```

- **Ejecutar interprete multilínea con timer:**

```sh
python main.py --multiline --timer
```

Para evaluar la performance de nuestra implementación comparándola con la implementación de JS corriendo node ejecutamos la función **fib(20)** medimos un tiempo de 1353.58 ms mientras que la ejecución en JS real tardo 1.34 ms (alrededor de 1000 veces menos).

Esto es por el motivo que vimos en clase, al agregarle más capas de abstracción hasta ser traducido a código máquina notamos que la performance se ve afectada. Sumado a esto al haber implementado el intérprete sin compilación demora más.

Si se desea comparar copiar la función fib y ejecutarla con los parámetros mencionados previamente y para correr la versión real en JS ejecutar el siguiente comando:

```sh
node language_performance.js
```

Además se adjunta el script con instrucciones representativas del lenguaje que puede ser copiado y enviado al intérprete con la opción multilínea **(language_script.js)**

## Explicación de funcionalidades implementadas

Para el desarrollo de este interprete de JS construido en Python se usó como base la implementación plox vista en clase. Notar que la implementación de ciertas partes va a ser muy similar a lo visto en clase, a continuación, se especifican las funcionalidades diferenciales que tuvimos que implementar respecto a lo visto en clase para interpretar JS.

### 1. Tipos de Variables (`var`, `let`, `const`)

A diferencia de Lox, en JS existen distintos tipos de variable con comportamientos distintos.

#### Diferencias principales

| Tipo      | Reasignable | Redeclarable | Scope          |
| --------- | ----------- | ------------ | -------------- |
| **var**   | Sí          | Sí           | Function scope |
| **let**   | Sí          | No           | Block scope    |
| **const** | No          | No           | Block scope    |

En nuestra primera versión hicimos una simplificación, donde la principal diferencia es que const no puede ser reasignada mientras que las demás si.

Posteriormente cuando introdujimos conceptos más complejos de JS **(Ver sección Hoisting)** se avanzó con la implementación del resto de diferencias.

#### Principales modificaciones:

- **Scanner**: para mapear a cada tipo de variable como token distinto.
- **Parser**: para agregar la información de que la variable es constante.
- **Env**: para agregar el control al momento de definir una variable.

### 2. Representación de ausencia de valor:

JS tiene dos formas de representar la ausencia de valor, para representar la ausencia implicita o no especificada explícitamente (como por ejemplo el valor que retornan los llamados de las funciones si no se define un valor de retorno), se usa **undefined**.

Tambien este valor muchas veces se devuelve en lugar de retornar errores por ejemplo al acceder a propiedades inexistentes en un objeto, JS en ese sentido es bastante permisivo y evita en lo posible arrojar excepciones.

Por otro lado, cuando queremos representarlo de manera explícita debemos usar el valor **null**.

Para esto incorporamos una nueva instancia única (Singleton) que representa este valor, mientras que el None de Python lo traducimos a null.

#### Principales modificaciones:

- **Function**: el return value de las funciones si no se especifica es undefined.
- **Scanner**: para agregar los dos tokens.
- **Parser**: para devolver el valor literal undefined.
- **Intérprete**: para el manejo de estos valores (por ejemplo, el valor de truthiness de null y undefined es falsy) y en la coerción de tipos que se explicará a continuación.

### 3. NaN y coerción de tipos:

Como dijimos antes, JS es un lenguaje bastante tolerante a errores. Resumidamente esto se debe a que el lenguaje fue inicialmente pensado únicamente para agregar interactividad a navegadores (actualmente usado también en backend y varias otras cosas) la idea era que los errores no sean bloqueantes para la experiencia del usuario.

Por este motivo el lenguaje opta por implementar la coerción de tipos en lugar de arrojar excepciones al operar con distintos tipos como sí lo hace el lenguaje visto en clase.

Por ejemplo, en la suma si alguno de los dos es una cadena se interpreta como una concatenación de valores. En caso contrario se hace el casteo a número y si el valor no es interpretable como un numero valido en lugar de arrojar error se devuelve el valor NaN. Notar que muchas de las operaciones en las que se usa NaN devuelven este mismo valor.

#### Principales modificaciones:

- **Intérprete**: la mayoría de cambios fue acá, principalmente se modificó las expresiones binarias (agregando el manejo de las distintas operaciones entre distintos tipos de dato).

### 4. Distintas formas de igualdad:

A diferencia de lo que vimos en Lox, JS tiene 2 formas distintas de obtener la igualdad entre los valores. La igualdad "==" implica una coerción de tipos al comparar los valores, mientras que "===" no.

#### Principales modificaciones:

- **Scanner**: agregar tokens para distinguir las 2 igualdades.
- **Parser**: para devolver la expresión binaria.
- **Intérprete**: para implementar las 2 formas de comparar los valores.

### 5. Hoisting, TDZ y Shadowing:

#### Principales modificaciones:

El lenguaje tiene un manejo de scopes bastante más complejo que Lox, por eso para implementar un manejo similar del scope de las variables tuvimos que modificar principalmente dos componentes del sistema, el **Resolver** (para contemplar este manejo en el análisis estático del código y registrar el scope de cada variable) y el **Intérprete** para ejecutar las instrucciones contemplando el manejo de forma correcta.

#### Más información:

Para el manejo de scopes hay 2 conceptos principales que tuvimos que profundizar, el hoisting y el temporal dead zone.

El primero implica que en JS las variables son registradas al comienzo del scope antes de la ejecución del código teniendo un valor por defecto de undefined. Luego al momento de llegar a la linea donde se hizo la definición de esta se asigna el valor correspondiente.

Aunque parezca poco intuitivo este comportamiento permite ejecutar instrucciones usando la variable, aunque se haya declarado en una etapa posterior. Esto unicamente aplica a variables de tipo "var" y las funciones declaradas que no sean function expression (funciones asignables a variables, tambien implementadas en esta etapa).

Por otro lado, las variables de tipo "let" y "const" tienen un comportamiento similar, en el que se registran las variables al tope de su block scope (a diferencia de "var" que se mueve al scope de la funcion).

A pesar de ser registradas son inutilizables antes de que se declaren arroja un error de sintaxis. Para detectar este tipo de caso introducimos una nueva clase Singleton **TDZ**, que básicamente es un valor guarda que indica que todavía no se llegó a la declaración de la variable.

Además nuestra implementación soporta **Shadowing** (la capacidad de volver a declarar una variable que fue declarada en un scope anterior, esto impide que podamos acceder a la variable declarada antes) .

Este manejo de scopes se lleva a cabo previo a la ejecución de las instrucciones ingresadas.

### 6. Keyword Typeof:

Como muchos lenguajes, JS necesita una forma de obtener el tipo de dato en tiempo de ejecución. Así que implementamos el operador `typeof` que retorna un string indicando el tipo del operando.

**Ejemplo:**

```javascript
typeof 42;           // "number"
typeof "hola";       // "string"
typeof true;         // "boolean"
typeof undefined;    // "undefined"
typeof null;         // "object" (comportamiento peculiar de JS)
typeof [];           // "object"
typeof {};           // "object"
typeof function(){}; // "function"
```

#### Principales modificaciones:

Tuvimos que modificar:
- **Scanner**: el token `TYPEOF`.
- **Parser**: que devuelve una expresión unaria.
- **Intérprete**: donde va la lógica para determinar el tipo.

### 7. Interpolación de template literals:

Los template literals son un feature muy común hoy en día. En JS, la interpolación funciona como si fuera concatenación de strings. Así que decidimos hacerlo como syntax sugar: el parser los traduce a concatenaciones con `+`.

**Ejemplo:**

```javascript
let nombre = "mundo";
let mensaje = `Hola, ${nombre}!`;  // Se traduce a: "Hola, " + nombre + "!"
```

Y en la evaluación, simplemente hacemos concatenación normal.

#### Principales modificaciones:

Modificamos:
- **Scanner**: mapea backticks y lo que va en `${}`.
- **Parser**: traduce a concatenaciones con `+`.

### 8. Nullish operator:

El `??` es parecido al `||` pero más preciso. Mientras que `||` considera todo lo falsy (`0`, `""`, `false`, etc.), el `??` solo considera `null` y `undefined`. Muy útil cuando querés un default pero tenés valores como `0` o strings vacíos que son válidos.

**Ejemplo:**

```javascript
let a = null;
let b = a ?? "valor por defecto";  // "valor por defecto"

let c = 0;
let d = c ?? "valor por defecto";  // 0 (porque 0 no es null/undefined)

let e = undefined;
let f = e ?? "valor por defecto";  // "valor por defecto"
```

**Comparación con ||:**

```javascript
// || considera todos los valores falsy
console.log(0 || 5);           // 5
console.log(0 ?? 5);           // 0

// ?? solo considera null y undefined
console.log("" || "default");  // "default"
console.log("" ?? "default");  // ""
```

#### Principales modificaciones:

Cambios puntuales:
- **Scanner**: token para `??`.
- **Parser**: devuelve una expresión lógica.
- **Intérprete**: implementa la lógica de nullish coalescing.

### 9. Arrow functions:

Básicamente son syntax sugar de function expressions. Se comportan igual en la mayoría de casos, así que la solución fue simple: el parser las traduce a function expressions y listo.

**Ejemplo:**

```javascript
// Arrow function
const sumar = (a, b) => a + b;

// Es lo mismo que:
const sumarExpr = function(a, b) { return a + b; };

// Con un parámetro, sin paréntesis
const doble = x => x * 2;

// Sin parámetros
const aleatorio = () => Math.random();
```

#### Principales modificaciones:

Realmente simple:
- **Parser**: traduce arrow → function expression.

### 10. Arrays:

Listas de elementos. Queríamos que fueran simples pero potentes: cualquier tipo de dato, indexación desde 0, y auto-extensión cuando asignas a índices futuros.

**Características principales:**

- **Indexación**: acceso mediante índices numéricos (desde 0).
- **Propiedad .length**: te dice cuántos elementos hay.
- **Auto-extensión**: si asignas a `arr[10]` cuando solo hay 3 elementos, se expande automáticamente.
- **Elementos heterogéneos**: un array puede mezclar números, strings, booleanos, lo que sea.

**Ejemplo:**

```javascript
let arr = [1, "dos", true, null];
console.log(arr[0]);        // 1
console.log(arr.length);    // 4
arr[5] = "elemento 5";      // Auto-extensión
console.log(arr.length);    // 6
console.log(arr[3]);        // undefined (posición vacía)

// Arrays anidados
let matriz = [[1, 2], [3, 4]];
console.log(matriz[0][1]);  // 2

// Con funciones
let numeros = [1, 2, 3];
let resultado = numeros[0] + numeros[1];  // 3
```

#### Principales modificaciones:

Tuvimos que agregar:
- **Expressions.py**: la clase `ArrayExpression`.
- **Parser.py**: parseamos `[...]` en `primary()`.
- **Interpreter.py**: `ArrayExpression` → listas de Python, con indexación y `.length`.
- **Resolver.py**: resolver recursivo.

### 11. Objects:

Colecciones de pares clave-valor. Una forma natural de agrupar datos relacionados.

**Ejemplo:**

```javascript
let persona = {
  nombre: "Juan",
  edad: 30,
  contacto: {
    email: "juan@gmail.com",
    telefono: "1234567890"
  }
};

console.log(persona.nombre);           // "Juan"
console.log(persona["edad"]);          // 30
console.log(persona.contacto.email);   // "juan@gmail.com"

// Propiedades dinámicas
persona.ciudad = "Buenos Aires";
console.log(persona.ciudad);           // "Buenos Aires"

// Arrays de objetos
let usuarios = [
  { id: 1, nombre: "Ana" },
  { id: 2, nombre: "Bruno" }
];
console.log(usuarios[0].nombre);  // "Ana"
```

#### Principales modificaciones:

Modificaciones:
- **Expressions.py**: `ObjectLiteral` para los pares.
- **Parser.py**: parseamos `{...}` en `primary()`, con lookahead para distinguir bloques de objetos.
- **Interpreter.py**: → diccionarios de Python.
- **Resolver.py**: resolver recursivo.

### 12. Member Access:

Una vez que tenés arrays y objetos, necesitás acceder a sus elementos. El acceso funciona con notación de punto, corchetes, chaining, propiedades computadas y hasta con strings.

**Ejemplo:**

```javascript
let obj = {
  a: { b: { c: 10 } },
  arr: [1, 2, 3]
};

// Chaining (múltiples accesos encadenados)
console.log(obj.a.b.c);           // 10
console.log(obj.arr[0]);          // 1

// Propiedades computadas
let propiedad = "b";
console.log(obj.a[propiedad].c);  // 10

// Strings (indexación de caracteres)
let str = "JavaScript";
console.log(str[0]);              // "J"
console.log(str[4]);              // "S"

// Propiedades inexistentes retornan undefined
console.log(obj.x);               // undefined
console.log(obj.y.z);             // Error! (obj.y es undefined)
```

#### Principales modificaciones:

Los cambios:
- **Expressions.py**: `MemberExpression` (`object`, `property`, `computed`).
- **Parser.py**: refactorizamos `call()` con while para manejar chaining.
- **Interpreter.py**: evaluación del objeto y propiedad, con `.length` y `undefined` para inexistentes.
- **Resolver.py**: resolver recursivo.

### 13. Assignment Operators:

Syntactic sugar: `x += 5` en vez de `x = x + 5`. Mucho más cómodo de escribir.

**Operadores disponibles:**

| Operador | Equivalente a |
|----------|--------------|
| `+=` | `a = a + b` |
| `-=` | `a = a - b` |
| `*=` | `a = a * b` |
| `/=` | `a = a / b` |
| `%=` | `a = a % b` |

**Ejemplo:**

```javascript
let x = 10;
x += 5;      // x = 15

let arr = [10, 20, 30];
arr[0] *= 2; // arr[0] = 20

let obj = { valor: 100 };
obj.valor -= 25; // obj.valor = 75
```

#### Principales modificaciones:

Cambios distribuidos:
- **Token.py**: cinco tokens nuevos.
- **Scanner.py**: reconoce `+=`, `-=`, etc.
- **Expressions.py**: `Assignment` con targets variables o `MemberExpression`.
- **Parser.py**: detecta y convierte a operaciones binarias.
- **Interpreter.py**: evalúa assignments con targets complejos.
- **Resolver.py**: resuelve los targets.

### 14. Control Flow (if/else, while, for, break, continue):

Sin control de flujo no hay mucho que hacer. Implementamos lo básico: condiciones, bucles, y forma de salir de ellos.

**Ejemplo:**

```javascript
// if/else
if (x > 10) {
  console.log("Mayor");
} else {
  console.log("Menor");
}

// while
let i = 0;
while (i < 5) {
  console.log(i);
  i++;
}

// for
for (let j = 0; j < 3; j++) {
  if (j === 1) continue;  // salta
  if (j === 2) break;     // termina
  console.log(j);
}
```

#### Principales modificaciones:

Todo lo necesario:
- **Stmt.py**: clases para cada tipo de statement.
- **Scanner**: reconoce las palabras clave.
- **Parser**: parsea la sintaxis.
- **Interpreter**: ejecuta, con excepciones para break/continue.

### 15. Functions:

El corazón del lenguaje. Reutilización de código, encapsulación, pasar behavior. Y lo mejor: closures que capturan el scope externo.

**Ejemplo:**

```javascript
// Declaración (con hoisting)
function sumar(a, b) {
  return a + b;
}
console.log(sumar(2, 3));  // 5

// Expresión y arrow function
const restar = (a, b) => a - b;
console.log(restar(10, 3));  // 7

// Closures (capturan scope externo)
function crearContador() {
  let count = 0;
  return function() {
    count++;
    return count;
  };
}

let contador = crearContador();
console.log(contador());  // 1
console.log(contador());  // 2
console.log(contador());  // 3

// Callbacks
function procesar(valor, callback) {
  return callback(valor * 2);
}
console.log(procesar(5, x => x + 10));  // 20
```

#### Principales modificaciones:

Bastantes cambios:
- **Expressions.py**: `FunctionExpression` para anónimas.
- **Stmt.py**: `FunctionStmt` para declaradas.
- **Function.py**: la clase que encapsula funciones JS con su ambiente.
- **Parser.py**: parsea ambas.
- **Resolver.py**: hoisting y closures.
- **Interpreter.py**: crea `Function`, bindea closures, maneja returns.
