sudo apt update
sudo apt install -y chromium-browser
pip install ./deck_scraper
python backend/manage.py migrate
python backend/manage.py
gunicorn backend.wsgi