apt-get update
apt-get install -y git-lfs
git lfs install
git lfs pull
cd backend
python myapp/static/json/get_and_process.py
python manage.py makemigrations --noinput
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py import_cards
gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 2