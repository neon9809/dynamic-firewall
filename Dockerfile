# dynamic-firewall Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Create directories for config and data
RUN mkdir -p /app/config /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Make main.py executable
RUN chmod +x /app/app/main.py

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import sqlite3; conn = sqlite3.connect('/app/data/ips.db'); conn.close()" || exit 1

# Run the application
CMD ["python", "-u", "/app/app/main.py"]
