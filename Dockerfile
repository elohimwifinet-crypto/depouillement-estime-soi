FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Répertoire de données persistantes (à monter en volume sur RouterOS)
ENV APP_DATA_DIR=/app/data
RUN mkdir -p /app/data

EXPOSE 5000

# Identifiants admin par défaut à la première création de la base
# (à changer immédiatement via /admin/users une fois connecté)
ENV ADMIN_USERNAME=admin
ENV ADMIN_PASSWORD=admin123

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
