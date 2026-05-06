set -e
gunicorn project.wsgi --log-file -