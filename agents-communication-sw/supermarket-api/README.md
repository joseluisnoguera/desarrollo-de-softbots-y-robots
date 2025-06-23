# API Supermarket

Esta aplicación es una API RESTful escrita en Golang que simula la gestión de inventario de un supermercado.

## Tecnologías

- Golang
- SQLite
- gorilla/mux

## Endpoints de la API

- `GET /items`: Lista todos los items con sus existencias.
- `POST /items`: Compra una cantidad específica de un item, disminuyendo sus existencias.
- `PUT /items`: Repone la cantidad de un item a su máximo de existencias.

Cada ítem tiene un id, un nombre, un precio, una cantidad de existencias, y un límite máximo que pueden haber de existencias

Además, esta API está preparada para ser usada por un Agente con MCP.

## Cómo ejecutar localmente

1.  Asegúrate de tener Go (versión 1.24 o superior) instalado en tu sistema.
2.  Instala las dependencias del proyecto ejecutando el siguiente comando en la raíz del proyecto:
    ```bash
    go mod tidy
    ```
3.  Ejecuta la API en el puerto 3005 usando Make:
    ```bash
    make run
    ```
    O directamente con Go:
    ```bash
    go run main.go
    ```

## Ejemplos de Uso

### Listar todos los items

**Request:**
```http
GET /items
```

### Comprar un item

Reduce el stock de uno o más items especificados por su ID.

**Request:**
```http
POST /items
```

**Body:**
```json
[
    {
        "id": 1,
        "quantity": 5
    },
    {
        "id": 2,
        "quantity": 10
    }
]
```

### Reponer un item

Aumenta el stock de uno o más items especificados por su ID con una cantidad determinada.

**Request:**
```http
PUT /items
```

**Body:**
```json
[
    {
        "id": 1,
        "quantity": 20
    },
    {
        "id": 3,
        "quantity": 15
    }
]
```