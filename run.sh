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
python backend/manage.py migrate
python backend/manage.py
gunicorn backend.wsgi --workers 2 --threads 1