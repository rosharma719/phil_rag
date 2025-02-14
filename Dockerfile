# Use a slightly older, more stable Python version
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (needed for FAISS and others)
RUN apt-get update && apt-get install -y \
    swig \
    libopenblas-dev \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application  
COPY . .

# Default to interactive mode
CMD ["bash"]
