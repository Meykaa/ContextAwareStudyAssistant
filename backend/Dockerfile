# Use the latest Python version with a slim image
FROM python:3.11-slim

# Set environment variables to ensure proper functioning
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Update and upgrade the base image to install any security patches
RUN apt-get update && apt-get upgrade -y && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install dependencies from the requirements file
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire application into the container
COPY . /app/

# Expose the port your app will be running on
EXPOSE 5000

# Command to run your app (replace 'app.py' with the main entry point of your app)
CMD ["python", "app.py"]
