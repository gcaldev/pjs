# PJS

Implementación en Python de un subset de Javascript.

Se recomienda el uso de [Black](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) para formateo de código.

```sh
black .
```

## Scanner

Componente encargado de tomar el texto ingresado y transformarlo a tokens correspondientes a un subset del lenguaje.

- **Ejecutar tests:**

```sh
python -m pytest -q
```

- **Ejecutar scanner en modo interactivo:**

```sh
python main.py
```

Se pedirá una línea de código como entrada; el scanner devolverá los tokens reconocidos.
