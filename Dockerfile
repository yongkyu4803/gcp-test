FROM python:3.9-slim

# Chrome 설치 및 의존성 추가
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    fonts-nanum \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Chrome WebDriver 설정
ENV CHROME_VERSION=$(google-chrome --version | awk '{ print $3 }' | awk -F'.' '{ print $1 }')

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일 복사
COPY requirements.txt .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# Chrome 옵션 환경변수 설정
ENV CHROME_OPTIONS="--headless --disable-gpu --no-sandbox --disable-dev-shm-usage --disable-software-rasterizer"

# 포트 설정
ENV PORT 8080

# 실행 명령
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app