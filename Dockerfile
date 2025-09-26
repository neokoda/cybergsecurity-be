FROM python:3.11-slim

# Set the working directory
WORKDIR /neocontract-be

RUN apt-get update && apt-get install -y \
    build-essential gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*
# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the application port
EXPOSE 8080

# Run the application
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload" ]