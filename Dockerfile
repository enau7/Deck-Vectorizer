FROM python:3.13

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY requirements.txt .
COPY . .

# Install git lfs
RUN apt-get update
RUN apt-get install -y git-lfs
RUN git lfs install
RUN git lfs pull

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install ./deck_scraper

# Migrate static files
WORKDIR /app/backend
RUN python manage.py migrate
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "1", "--threads", "2"]