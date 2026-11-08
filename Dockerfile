FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x docker-entrypoint.sh \
    && DJANGO_SECRET_KEY=build DJANGO_DEBUG=0 python manage.py collectstatic --noinput

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=3s --retries=5 \
  CMD python -c "import urllib.request,sys; urllib.request.urlopen('http://127.0.0.1:8000/api/health/')" || exit 1
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "web_application.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
