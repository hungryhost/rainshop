#!/bin/sh
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi
echo "from django.contrib.auth import get_user_model;
User = get_user_model()
if not User.objects.filter(email='$DJANGO_ADMIN_EMAIL').exists(): User.objects.create_superuser(username='$DJANGO_ADMIN_USERNAME', email='$DJANGO_ADMIN_EMAIL', password='$DJANGO_ADMIN_PASSWORD')" | python manage.py shell

python manage.py migrate
python manage.py loaddata products.json --app products.Products
exec "$@"