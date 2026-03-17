# ========================================================
# Developer - @usrhtff009
# Channel - https://t.me/usrht01
# ========================================================

FROM python:3.10.13-slim-bullseye

# Prevent Python from creating .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure logs are shown instantly
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies for high-performance (TGCrypto Support)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies separately to use Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files to the container
COPY . .

# Launch the application
# Note: Ensure bot.py contains the entry logic for your bot
CMD ["python3", "bot.py"]

# ========================================================
# Optimized for Cloud Deployment (Render/VPS/Railway)
# Developer - @usrhtff009 | Channel - https://t.me/usrht01
# ========================================================
