# Use an official JDK runtime as a parent image
FROM openjdk:20-slim

# Install Python.
RUN apt-get update
RUN apt-get install -y python3 python3-pip

RUN java -version
RUN python3 --version

# Set the working directory in the container
WORKDIR /app

# Add the current directory contents into the container at /app
ADD code-ai-agents-service-app-0.3.95 /app

ENV HOST=0.0.0.0
ENV PORT=5050

# Make port 5050 available to the world outside this container
EXPOSE 5050

# Run main.py when the container launches
CMD ["./bin/AgentService"]