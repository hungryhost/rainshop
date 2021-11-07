# RainShop app
### Deployed at https://projects.rainforest.yuryborodin.ru/
### Swagger: https://projects.rainforest.yuryborodin.ru/api/v1/swagger/
### ReDoc: https://projects.rainforest.yuryborodin.ru/api/v1/redoc/

## Stack:
- Python: 3.8.6
- Django + DRF

(for more details on used packages see rainshop/requirements.txt)

## Deployment
The process of deployment is quite simple and consists of 3 stages:
1. Set up .env file for postgres container. Example:

```
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=postgres_password
POSTGRES_DB=rainshop
```
2. Set up .env file for the app itself. Example:
```
# base settings
DJANGO_ADMIN_USERNAME=test
DJANGO_ADMIN_PASSWORD=test
DJANGO_ADMIN_EMAIL=test@test.com
DEBUG=<on/off>
SQL_DEBUG=<True/False>
ALLOWED_HOSTS=127.0.0.1,.localhost
SECRET_KEY=<secret_key>
CORS_ORIGIN_ALLOW_ALL=<True, False>
CORS_ALLOWED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
# log paths
LOG_ROOT=<log files root if needed>
# database config
DB_NAME=rainshop
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres_user
DB_PASSWORD=postgres_password
# storage settings
USE_POSTGRES=True
USE_S3=False
USE_REDIS_CACHE=False
```
3. Build and start up the containers with ```docker-compose up -d```. Default mapping
is to 127.0.0.1:8081, but could be changed in the docker-compose.yml file.
## Example usage
Usage of the app is quite simple as well.
### Obtain token 
Obtain token for the user via ```POST /api/v1/token/```
Example request body:
```
{
    "username": "test",
    "password": "test"
}
```

The token is used after in the Authorization header as
```Token <token>```
### Add product (requires authentication)
Add a product to the app via ```POST /api/v1/products/``` endpoint.
Example request body:
```
{
    "name": "PS5",
    "cost": 300.00,
    "price": 500.00,
    "quantity": 20
}
```

### List products
List products via ```GET /api/v1/products/``` endpoint.
Example request body:
```
{
    {
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 8,
            "name": "Esterified Estrogens and Methyltestosterone",
            "cost": "283.00",
            "price": "569.00",
            "quantity": 58,
            "cost_currency": "USD",
            "price_currency": "USD",
            "self": "http://127.0.0.1:8000/api/v1/products/8/"
        },
        {
            "id": 9,
            "name": "Duet DHA",
            "cost": "278.00",
            "price": "593.00",
            "quantity": 68,
            "cost_currency": "USD",
            "price_currency": "USD",
            "self": "http://127.0.0.1:8000/api/v1/products/9/"
        }
    ]
    }
}
```

### Add product to your cart (requires authentication)
Add a product via ```POST /api/v1/cart/``` endpoint.
Example request body:
```
{
    "product_id": 1,
    "quantity": 1
}
```
Example response:

```
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 7,
            "product": {
                "id": 10,
                "name": "CYPROHEPTADINE HYDROCHLORIDE",
                "price": "607.00",
                "self": "https://projects.rainforest.yuryborodin.ru/api/v1/products/10/"
            },
            "quantity": 1,
            "max_quantity": 21,
            "is_available_as_selected": true,
            "total_price": "607.00",
            "self": "https://projects.rainforest.yuryborodin.ru/api/v1/cart/7/"
        }
    ]
}
```
### Place order (requires authentication)
Place order via ```POST /api/v1/cart/``` endpoint with __empty request body__.

### Mimic payment via dummy endpoint
Mimic payment callback for the specific order via ```GET api/v1/orders/{id}/payment-callback/ ```.
Changes the order's status to "PAYED".

### See stats 
See stats via ```POST /api/v1/products/stats/?start_date=2021-11-01&end_date=2021-11-07```.

*Query parameters are optional.*

Example response:
```
{
    "total_orders": 5,
    "total_ordered": {
        "CENTER-AL - AMBROSIA ACANTHICARPA POLLEN": 25,
        "Duet DHA": 5,
        "Calcitriol": 11,
        "PROPRANOLOL HYDROCHLORIDE": 4
    },
    "total_returned": {
        "CENTER-AL - AMBROSIA ACANTHICARPA POLLEN": 2,
        "Duet DHA": 5,
        "PROPRANOLOL HYDROCHLORIDE": 4
    },
    "orders_by_status": {
        "total_created": 0,
        "total_cancelled": 1,
        "total_payed": 3
    },
    "orders_by_monetary_stats": {
        "total_gross_income": {
            "CENTER-AL - AMBROSIA ACANTHICARPA POLLEN": 21091.0,
            "Duet DHA": null,
            "Calcitriol": 3850.0
        },
        "total_cost": {
            "CENTER-AL - AMBROSIA ACANTHICARPA POLLEN": 188.0,
            "Calcitriol": 177.0
        },
        "total_income": {
            "CENTER-AL - AMBROSIA ACANTHICARPA POLLEN": 20903.0,
            "Calcitriol": 3673.0
        }
    }
}
```

*Full documentation is available at https://projects.rainforest.yuryborodin.ru/api/v1/swagger/ or
https://projects.rainforest.yuryborodin.ru/api/v1/redoc/*


## Possible Improvements
- Cancel/Refund operations could be moved to their respective celery tasks (mainly 
  for the process of "restocking" - updating product quantity info).
  