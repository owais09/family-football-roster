FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including Chrome for Selenium and Xvfb for virtual display
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    ca-certificates \
    xvfb \
    x11-utils \
    && wget -q -O /tmp/google-chrome-stable_current_amd64.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y /tmp/google-chrome-stable_current_amd64.deb \
    && rm /tmp/google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Set up virtual display for pywhatkit
ENV DISPLAY=:99

# Copy application files first
COPY . .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create .streamlit directory for config
RUN mkdir -p .streamlit

# Make startup script executable
RUN chmod +x start.sh

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run startup script
CMD ["./start.sh"]
