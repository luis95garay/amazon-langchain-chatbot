# Use the official Python 3.9 image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files
COPY requirements.txt ./requirements.txt

# Install any dependencies specified in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src

# Install any dependencies specified in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Expose the ports for each API (adjust the port numbers as needed)
EXPOSE 9000

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "9000", "src.main:app"]
