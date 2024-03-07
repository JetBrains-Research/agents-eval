# Use an official Python runtime as a parent image
FROM python:3.8-slim-buster

# Set the working directory in the container
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5050

# Make port 5050 available to the world outside this container
EXPOSE 5050

# Run main.py when the container launches
CMD ["python", "file_system_service.py"]