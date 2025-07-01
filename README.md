# Django app - Online store of seeds and equipment for growing microgreens
The application includes:
- Store app
- Admin interface for store management

## Functionality
- Product catalog with categories
- Product filtering
- Search by product, price, cultivation difficulty
- Cart for order formation
- Promo codes for purchase (discount percentage, fixed discount, number of uses, minimum price for using a promo code)
- Payment for goods via Yookassa, webhook accepts a response from Yookassa
- Email notification about order status
- Login and registration (setting up access depending on user type)
- User profile (password change, recent orders, credentials, employee and customer profiles)
- Information pages
- Blog with articles on products displaying popular articles

## Technologies
- Django
- PostgreSQL
- Celery
- Redis
- Docker

## External modules
- yookassa (for payment integration)
- django-ckeditor-5 (editor for the blog and pages apps)

# Getting Started
## Prerequisites
- Python 3.11 or higher
- Poetry (Python dependency management)
## Installation
- Clone the repository:
```
git clone https://github.com/vld-bgdn/store_of_seeds.git
cd store_of_seeds
```
- Install dependencies using Poetry:
- Install Poetry if you don't have it already
```
curl -sSL https://install.python-poetry.org | python3 -
```
- Install project dependencies
```
poetry install
```
- Activate the virtual environment:
```
poetry shell
```
- Set up env file for app (use your own values)
```
cat > ./.env << 'EOL'
DB_HOST=""
POSTGRES_DB=""
POSTGRES_USER=""
POSTGRES_PASSWORD=""
EMAIL_HOST=""
EMAIL_PORT=""
EMAIL_USE_TLS=""
EMAIL_USE_SSL=""
EMAIL_HOST_USER=""
EMAIL_HOST_PASSWORD=""
DEFAULT_FROM_EMAIL=""
SECRET_KEY=""
CELERY_BROKER_URL=""
CELERY_RESULT_BACKEND=""
YOOKASSA_SHOP_ID=""
YOOKASSA_SECRET_KEY=""
EOL
```
### ENV descriptions
| Name                     | Description                                                                                       |
|--------------------------|---------------------------------------------------------------------------------------------------|
| `DB_HOST`                | database host. Example: localhost                                                                 |
| `POSTGRES_DB`            | database name                                                                                     |
| `POSTGRES_USER`          | database user                                                                                     |
| `POSTGRES_PASSWORD`      | database password                                                                                 |
| `EMAIL_HOST`             | email host. Example: smtp.yandex.ru                                                               |
| `EMAIL_PORT`             | email server port. Example: 465                                                                   |
| `EMAIL_USE_TLS`          | email server TLS option, boolean. Example: False                                                  |
| `EMAIL_USE_SSL`          | email server SSL option, boolean. Example: True                                                   |
| `EMAIL_HOST_USER`        | username to access the email server. Example: no-reply@domain.com                                 |
| `EMAIL_HOST_PASSWORD`    | user password to access the email server                                                          |
| `DEFAULT_FROM_EMAIL`     | default email address for FROM field                                                              |
| `SECRET_KEY`             | secretkey to protect signed data in the Django                                                    |
| `CELERY_BROKER_URL`      | redis url for celery. Example: `redis://localhost:6379/0`                                         |
| `CELERY_RESULT_BACKEND`  | redis url for celery results. Example: `redis://localhost:6379/1`                                |
| `YOOKASSA_SHOP_ID`       | yookassa shop id for payment. Get it on the yookassa account: `https://yookassa.ru/my/profile`    |
| `YOOKASSA_SECRET_KEY`    | yookassa secret key for payment. Get it on the yookassa account: `https://yookassa.ru/my/profile` |

To generate django secret key use following command:

```
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```
- Set up the database:
```
docker-compose up -d db
python manage.py migrate
```
- Create a superuser:
```
python manage.py createsuperuser
```
Filling the DB with test data
```
python manage.py test_data
```
- Build and start all app services via docker
```
docker-compose up -d
```
- Visit http://127.0.0.1:8000/ in your browser to see the application.

# Project folder structure
```
├── apps
│   ├── accounts
│   │   └── migrations
│   ├── blog
│   │   └── migrations
│   ├── cart
│   │   └── migrations
│   ├── discounts
│   │   └── migrations
│   ├── orders
│   │   └── migrations
│   ├── pages
│   │   └── migrations
│   ├── products
│   │   ├── migrations
│   │   └── templatetags
│   └── reports
│       └── migrations
├── config
├── media
│   ├── avatars
│   ├── categories
│   └── products
├── static
└── templates
    ├── accounts
    ├── blog
    ├── cart
    ├── includes
    ├── orders
    │   └── email
    ├── pages
    ├── products
    └── reports
```

# License
MIT License © vld-bgdn
