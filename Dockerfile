# CFP Scout Docker Container
# Production-ready container with MCP support and scheduled execution

FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome and ChromeDriver for Selenium
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+') \
    && CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%%.*}") \
    && wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" \
    && unzip /tmp/chromedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm /tmp/chromedriver.zip

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY env.example .env.example

# Create necessary directories
RUN mkdir -p logs data

# Create non-root user for security
RUN useradd -m -s /bin/bash cfpscout \
    && chown -R cfpscout:cfpscout /app

# Switch to non-root user
USER cfpscout

# Environment variables with defaults
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV EXECUTION_MODE=hybrid
ENV SCHEDULE_TIME=08:00
ENV TIMEZONE=Europe/London

# Expose port for potential web interface
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 src/main.py --status || exit 1

# Default command - run in scheduled mode
CMD ["python3", "src/main.py", "--schedule"]

# Alternative entry points:
# Run once: docker run cfp-scout python3 src/main.py --run-once
# Traditional mode: docker run -e EXECUTION_MODE=traditional cfp-scout
# MCP mode: docker run -e EXECUTION_MODE=mcp cfp-scout
# Status check: docker run cfp-scout python3 src/main.py --status 