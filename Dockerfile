# Use an official Python image as the base image
FROM python:3.11-slim

ENV ENV cloud

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directoryyy
COPY src/ .

# Specify the command to run on container start
CMD ["python", "./app.py"]

EXPOSE 8080