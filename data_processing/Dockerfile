# Use the official Python 3.9 image as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy all files
COPY . .

# Install chrome driver
# RUN apt-get update -y
# RUN apt-get install -y wget xvfb gnupg unzip
# RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
# RUN echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
# RUN apt-get update -y
# RUN apt-get install -y google-chrome-stable
# ENV CHROMEDRIVER_DIR /chromedriver
# RUN mkdir $CHROMEDRIVER_DIR
# RUN wget -q --continue -P $CHROMEDRIVER_DIR "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/116.0.5845.96/linux64/chrome-linux64.zip"
# RUN unzip $CHROMEDRIVER_DIR/chrome* -d $CHROMEDRIVER_DIR
# ENV PATH $CHROMEDRIVER_DIR:$PATH

# Install any dependencies specified in the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Expose the ports for each API (adjust the port numbers as needed)
EXPOSE 9002

ENTRYPOINT ["uvicorn", "--host", "0.0.0.0", "--port", "9002", "main:app"]
