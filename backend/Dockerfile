FROM python:3.9-slim

WORKDIR /app

# Install git and other required system dependencies
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install custom LIDA from your repository
RUN pip install git+https://github.com/rayaran1000/lida-modified.git

# Copy the application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 