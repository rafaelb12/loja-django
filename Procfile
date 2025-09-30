release: pip install --upgrade pip && pip install -r requirements.txt
web: gunicorn loja.wsgi:application --bind 0.0.0.0:$PORT