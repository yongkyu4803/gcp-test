FROM python:3.9-slim

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    fonts-nanum \
    xvfb \
    gnupg \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set Chrome options
ENV PYTHONPATH="/app"
ENV CHROME_OPTIONS="--headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu"
ENV PORT=8080
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 앱 디렉토리를 볼륨으로 노출
VOLUME /app

# 포트 노출
EXPOSE 8080

# Run command - 직접 Flask 실행으로 변경
CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]