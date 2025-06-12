Step 1: Create and Run Migrations
First, you need to create migrations for your custom User model and then apply them:
# Create migrations for all apps
python manage.py makemigrations

# If you want to be specific about the users app:
python manage.py makemigrations users
# If you want to be specific about the orders app:
python manage.py makemigrations orders
# If you want to be specific about the blog app:
python manage.py makemigrations blog

# Apply the migrations to create the database tables
python manage.py migrate
Step 2: Create Superuser
After the migrations are successfully applied, you can create a superuser:
python manage.py createsuperuser
