# Simple Django store app
The application includes:
- Online store of seeds and equipment for growing microgreens
- Admin interface for store management
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
- Set up the database:
```
docker-compose up -d db
python manage.py migrate
```
- Create a superuser:
```
python manage.py createsuperuser
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
