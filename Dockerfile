FROM python:3.11-slim

# Set the working directory
WORKDIR /neocontract-be

# 1. Install necessary system packages for dependencies (like psycopg2)
# Keep this as a single layer for efficiency
RUN apt-get update \
    && apt-get install -y \
        build-essential \
        gcc \
        libpq-dev \
    # Clean up to keep the image small
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file before copying the whole app
COPY requirements.txt .

# 2. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# 3. **CRITICAL FIX**: Use $PORT for Cloud Run and bind to 0.0.0.0
# Cloud Run automatically sets the PORT environment variable.
# Your application MUST use this variable, not a hardcoded value.
# We remove ENV PORT=8080 and EXPOSE 8080 because the CMD handles the port.

# 4. **FIXED CMD**: Remove --reload and use gunicorn or the correct $PORT
# Use the gunicorn worker manager recommended for production (better performance and stability)
# If using gunicorn, ensure it's in your requirements.txt:
#CMD [ "gunicorn", "main:app", "--workers", "2", "--bind", "0.0.0.0:$PORT", "--worker-class", "uvicorn.workers.UvicornWorker" ]
CMD [ "sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT" ]
# OR, use a clean uvicorn command (ensure the port is read from $PORT)
#CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "$PORT" ]