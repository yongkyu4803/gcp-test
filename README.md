# 네이버 뉴스 크롤러

네이버 뉴스 검색 결과를 크롤링하여 Excel 파일로 저장하는 웹 애플리케이션입니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## Docker로 실행하기

1. Docker 이미지 빌드:
```bash
docker build -t naver-news-crawler .
```

2. Docker 컨테이너 실행:
```bash
docker run -p 8080:8080 naver-news-crawler
```

3. 브라우저에서 다음 주소로 접속:
```
http://localhost:8080
```

## 직접 실행하기

1. Python 앱 실행:
```bash
python app.py
```

2. 브라우저에서 다음 주소로 접속:
```
http://localhost:8080
```