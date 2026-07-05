FROM python:3.10-slim

WORKDIR /app

# Install system utilities (optional but helpful)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose port 8080 for Cloud Run
EXPOSE 8080

# Run Streamlit on port 8080 and bind to all interfaces headlessly
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]
