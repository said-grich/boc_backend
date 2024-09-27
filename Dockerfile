# Use the official Python image as a base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV OMP_THREAD_LIMIT=1



# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install Tesseract and other necessary packages
RUN apt-get update && apt-get install -y \
    git \
    tesseract-ocr \
    tesseract-ocr-ara \
    libtesseract-dev \
    libleptonica-dev \
    libreoffice \
    && apt-get clean

# Copy the rest of the application code into the container
COPY . /app/

# Expose the port Django will run on
EXPOSE 8000

# Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
