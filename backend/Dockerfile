# Use a minimal Python image
FROM python:3.11-slim

# Set environment variables to avoid .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt from the backend folder
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire backend folder into the container
COPY backend/ ./backend/

# Expose the port your Flask app will run on
EXPOSE 5000

# Command to run the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:app"]

