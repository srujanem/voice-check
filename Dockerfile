# syntax=docker/dockerfile:1
FROM python:3.10-slim

# Prevent interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    HOST=0.0.0.0

# Install system dependencies required for OpenCV, Librosa, and audio processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    libgl1 \
    libglib2.0-0 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /app

# Create a non-root user (Hugging Face standard UID 1000)
RUN useradd -m -u 1000 user && \
    chown -R user:user /app

# Copy requirements first for Docker layer caching
COPY --chown=user:user requirements.txt .

# Install Python packages (CPU-optimized PyTorch & TensorFlow)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code and models
COPY --chown=user:user . .

# Switch to non-root user
USER user

# Expose the default Hugging Face Spaces port
EXPOSE 7860

# Run the Waitress WSGI production server
CMD ["python", "run.py"]
