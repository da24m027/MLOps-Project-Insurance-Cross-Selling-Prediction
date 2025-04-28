# Use Python 3.9 slim image as base
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY . .

# Create directories for data
RUN mkdir -p /app/data /tmp/prometheus_multiproc_dir

# Set permissions for prometheus multiprocess directory
RUN chmod 777 /tmp/prometheus_multiproc_dir

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8000
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc_dir
ENV METRICS_ENABLED=true

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]