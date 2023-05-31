# Use an official Python runtime as the base image
FROM python:3.10-alpine

# Set the working directory in the container
WORKDIR /registration

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . /registration

# Set the command to run the application
CMD ["uvicorn", "main:app"]
