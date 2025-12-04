# Use Python 3.11 (has imghdr)
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (pdfplumber likes these for some PDFs)
RUN apt-get update && apt-get install -y \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Flask / gunicorn
EXPOSE 10000

# Start app with gunicorn
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:10000"]
