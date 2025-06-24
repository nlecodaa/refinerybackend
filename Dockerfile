# Use Python 3.10.14
FROM python:3.10.14-slim

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade-strategy eager -r requirements.txt


# Copy your backend app files
COPY . .

# Expose port (default Flask)
EXPOSE 5000

# Start the Flask server
CMD ["python", "api.py"]
