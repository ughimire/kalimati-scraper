FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the scraper code
COPY kalimati_scraper.py .

# Create data directory
RUN mkdir -p /app/data

# Set the entrypoint
ENTRYPOINT ["python", "kalimati_scraper.py"] 