sudo apt update
sudo apt install -y chromium-browser
sudo apt install -y \
    libnss3 \
    libgconf-2-4 \
    libxi6 \
    libxrender1 \
    libxrandr2 \
    libxss1 \
    libasound2 \
    libgtk-3-0
pip install ./deck_scraper
cd backend
python manage.py migrate
python manage.py collectstatic
python myapp/static/get_and_process.py
gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 2