# Use the official Python 3.9 image as the base image
FROM quay.io/unstructured-io/unstructured:latest
# FROM python:3.9-slim
# Set the working directory inside the container
WORKDIR /app

# Copy all files
COPY . .

# Install any dependencies specified in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/src

EXPOSE 9000 9002
# CMD ["bash"]

USER root
RUN chmod +x start.sh

CMD ["./start.sh"]
