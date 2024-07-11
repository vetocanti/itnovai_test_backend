# itnovai Test Backend

Backend for the itnovai test about a ecommerce. Develop in the framework FastAPI.
## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install -r requirements.txt
```

## How to run

```bash
fastapi dev main.py
```

## API

### Get all the products

```http
  GET /products/
```

| Parameter | Type     | Description                |

| :-------- | :------- | :------------------------- |

| `page` | `int` | **Optional**. page number of the product paginator by limit |

| `limit` | `int` | **Optional**. Amount of products by limit|


### Get all the products by category id

```http
  GET /products_category/:category_id
```

| Parameter | Type     | Description                |

| :-------- | :------- | :------------------------- |
| `page` | `int` | **Optional**. page number of the product paginator by limit |
| `limit` | `int` | **Optional**. Amount of products by limit|
| `category_id` | `int` | **Optional**. Id of the category|


### Get all the products that contain the name parameter in their names
```http
  GET /products_name/:name
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `page` | `int` | **Optional**. page number of the product paginator by limit |
| `limit` | `int` | **Optional**. Amount of products by limit|
| `name` | `String` | Input that could  be contain into some products name|

### Get all the categories of the products
```http
  GET /categories/
```
### Get all the categories of the products
```http
GET /products_id/:id
```
| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `id` | `int` |Product id |

## License

[MIT](https://choosealicense.com/licenses/mit/)
