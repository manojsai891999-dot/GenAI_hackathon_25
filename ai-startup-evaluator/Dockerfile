FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV DATABASE_URL=postgresql://app-user:aianalyst@/startup_evaluator?host=/cloudsql/startup-evaluator-db
ENV GCS_BUCKET_NAME=startup-evaluator-storage
ENV DEBUG=false

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main_agent.py"]
