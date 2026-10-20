FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Ensure storage directories exist
RUN mkdir -p uploads static

# Expose standard port
EXPOSE 8000

# Start server
CMD ["python", "run.py"]
