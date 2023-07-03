# Base image
FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the bot code to the container
COPY bot.py .

# Set environment variables
COPY .env .

# Run the bot code
CMD ["python3", "bot.py"]