# Use an official lightweight Python image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first (to leverage Docker caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
# COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# # Command to run the app
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

COPY start.sh .

RUN chmod +x start.sh

CMD ["./start.sh"]
