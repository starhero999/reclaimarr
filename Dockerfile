# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's code into the container at /app
COPY src/ /app/src/

# Define the entry point for the container.
# This will run the CLI tool when the container starts.
# Example: docker run my-image --media-path /data --dry-run
ENTRYPOINT ["python", "-m", "src.main"]
