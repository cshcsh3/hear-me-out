# Use Python 3.13 as the base image
FROM python:3.13.3-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy code into image
COPY pyproject.toml .
COPY src ./src

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir .

# Expose the port the app runs on
EXPOSE 3001

# Command to run the application
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "3001"] 