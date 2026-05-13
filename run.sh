pip install ./deck_scraper
cd backend
python myapp/static/json/get_and_process.py
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 2