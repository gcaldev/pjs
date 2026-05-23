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

Se implementa la expresión unaria que permite obtener el tipo de dato de un valor.

#### Principales modificaciones:

Para lograr esto agregamos el token que mapea el **Scanner**, el **Parser** para devolver una expresión unaria con este operador y el **Intérprete** para ejecutar esta nueva instrucción

### 7. Interpolación de template literals:

Para implementar esto pensamos en que la interpolación de JS se podría considerar como un syntax sugar de la concatenación de strings al usar la expresión binaria de suma. Entonces siguiendo lo que hicimos en clase con el for de Lox (traduciendolo a un while), decidimos implementarlo esta funcionalidad como syntax sugar de la concatenación de cadenas. Para llevar esto a cabo

#### Principales modificaciones:

El principal componente involucrado fue el **Parser**. También tuvimos que modificar el **Scanner** para mapear los nuevos tokens de template literals.

### 8. Nullish operator:

Este es un operador que muchos lenguajes tienen, faltante en el lenguaje de Lox. Es un operador similar al "||", que permite devolver la parte derecha si el valor izquierdo es null o undefined. Este operador es muy útil para asignar valores por defecto.

#### Principales modificaciones:

Los principales cambios para lograr implementarlo fueron agregar el mapeo a token en el **Scanner**, el **Parser** devuelve una expresión lógica nueva y la interpretación de esa nueva expresión en el Intérprete.

### 9. Arrow functions:

Para este tipo de funciones decidimos implementarlas como syntax sugar de las function expressions. Ya que a pesar de que hay algunos casos particulares (que para este tp no se tuvieron en cuenta como el funcionamiento en relacion al contexto de objeto **this**), en la mayoria de las cosas se comporta igual ya que es una función asignada como valor a una variable.

#### Principales modificaciones:

Para implementarla tuvimos que modificar el **Parser** para traducir los tokens de arrow function a una function expression.
