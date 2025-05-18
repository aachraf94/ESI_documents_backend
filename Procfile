web: python manage.py migrate --no-input && python manage.py collectstatic --no-input && gunicorn ESI_document_project.wsgi:application --bind 0.0.0.0:$PORT
