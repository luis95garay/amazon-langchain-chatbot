# Use the official Python 3.9 image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files
COPY . .

# Install any dependencies specified in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Navigate to the desired directory and run the shell commands
RUN cd /usr/local/lib/python3.9/site-packages/faiss && \
    ln -s -f swigfaiss.py swigfaiss_avx2.py

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "9000", "src.api.main:app"]
