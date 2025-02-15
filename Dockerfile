# Use a stable Python version
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (needed for FAISS and others)
RUN apt-get update && apt-get install -y \
    swig \
    libopenblas-dev \
    libomp-dev \
    python3 \
    python3-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment and upgrade pip
RUN python3 -m venv /app/venv && /app/venv/bin/pip install --upgrade pip

# Ensure the container always uses the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Copy dependencies and install them inside the virtual environment
COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Keep the container running interactively
CMD ["tail", "-f", "/dev/null"]
