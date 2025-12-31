FROM python:3.11-slim

# 1. Set up work directory and Python env flags
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Install GDAL system dependencies for Fiona + C toolchain
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      gdal-bin \
      libgdal-dev \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# 3. Explicitly point to gdal-config (usually on PATH anyway)
ENV GDAL_CONFIG=/usr/bin/gdal-config

# 4. Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copy your app code
COPY . .

# 6. Default startup command
CMD ["python", "app.py"]