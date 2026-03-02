FROM python:3.12-slim

# Install system deps for pdfplumber (poppler) and general build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory on the persistent volume mount point
RUN mkdir -p /data

# Expose port
EXPOSE 8080

# Run with gunicorn
CMD ["gunicorn", "-w", "2", "-b", "0.0.0.0:8080", "--timeout", "120", "--graceful-timeout", "5", "--access-logfile", "-", "web:create_app()"]
