# Use Python 3.12 Alpine as the base image
FROM python:3.12-alpine

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3000

# Start the application
CMD ["python", "server.py"]
