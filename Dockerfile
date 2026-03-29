FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose port (Render uses 10000 internally)
EXPOSE 10000

# Run everything at container start (FREE PLAN FIX)
CMD sh -c "python manage.py migrate && python manage.py createsu && python manage.py seed_data.py && python manage.py collectstatic --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:10000"