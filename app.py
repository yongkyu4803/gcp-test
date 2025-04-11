import os
import time
import base64
import io
import json
from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# 네이버 뉴스 크롤링 함수
def crawl_naver_news(search_keyword, scroll_count):
    news_data = []
    progress_info = {"current": 0, "total": scroll_count}
    
    # Chrome 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    options.add_argument('--window-size=1920,1080')
    
    # 웹드라이버 초기화
    try:
        service = Service()
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"웹드라이버 초기화 오류: {str(e)}")
        return []
    
    try:
        # 네이버 뉴스 검색 페이지로 이동
        driver.get(f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={search_keyword}")
        
        # 스크롤 및 데이터 수집
        for i in range(scroll_count):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            progress_info["current"] = i + 1
            
            # 뉴스 아이템 찾기
            news_items = driver.find_elements(By.CSS_SELECTOR, "li.bx")
            
            for item in news_items:
                try:
                    # 뉴스 정보 추출
                    title = item.find_element(By.CSS_SELECTOR, "a.news_tit").text
                    press = item.find_element(By.CSS_SELECTOR, "a.info.press").text
                    
                    # 시간 정보와 지면 정보 처리
                    time_info = ""
                    page_info = ""
                    info_spans = item.find_elements(By.CSS_SELECTOR, "span.info")
                    
                    for span in info_spans:
                        try:
                            if span.find_element(By.CSS_SELECTOR, "i.ico_paper"):
                                page_info = span.text
                        except:
                            if not span.find_elements(By.CSS_SELECTOR, "i"):
                                time_info = span.text
                    
                    # 네이버 뉴스 링크 확인
                    naver_news_link = ""
                    try:
                        naver_news_element = item.find_element(By.CSS_SELECTOR, "a.info[href*='news.naver.com']")
                        naver_news_link = naver_news_element.get_attribute("href")
                    except:
                        pass
                    
                    # 본문 설명 추출
                    description = item.find_element(By.CSS_SELECTOR, "div.dsc_wrap").text
                    
                    # 링크 추출
                    link = item.find_element(By.CSS_SELECTOR, "a.news_tit").get_attribute("href")
                    
                    # 뉴스 아이템 저장
                    news_item = {
                        'title': title,
                        'press': press,
                        'time': time_info,
                        'page_info': page_info,
                        'description': description,
                        'link': link,
                        'naver_news_link': naver_news_link
                    }
                    
                    # 중복 확인 후 추가
                    if news_item not in news_data:
                        news_data.append(news_item)
                        
                except Exception as e:
                    continue
        
    except Exception as e:
        print(f"크롤링 오류 발생: {str(e)}")
    
    finally:
        driver.quit()
    
    return news_data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crawl', methods=['POST'])
def crawl():
    try:
        data = request.get_json()
        search_keyword = data.get('search_keyword')
        scroll_count = int(data.get('scroll_count', 5))
        
        if not search_keyword:
            return jsonify({"error": "검색어를 입력해주세요."}), 400
        
        news_data = crawl_naver_news(search_keyword, scroll_count)
        
        if not news_data:
            return jsonify({"error": "검색 결과가 없습니다."}), 404
        
        return jsonify({
            "success": True,
            "count": len(news_data),
            "data": news_data,
            "sample": news_data[:3] if len(news_data) >= 3 else news_data
        })
    except Exception as e:
        return jsonify({"error": f"요청 처리 중 오류가 발생했습니다: {str(e)}"}), 500

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        news_data = data.get('news_data', [])
        search_keyword = data.get('search_keyword', 'naver_news')
        
        if not news_data:
            return jsonify({"error": "다운로드할 데이터가 없습니다."}), 400
        
        # DataFrame 생성
        df = pd.DataFrame(news_data)
        
        # 'page_info' 칼럼 제거
        if 'page_info' in df.columns:
            df = df.drop(columns=['page_info'])
        
        # 엑셀 파일 생성 - 더 안정적인 방식
        output = io.BytesIO()
        try:
            # 먼저 context manager 방식 시도
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
        except Exception as e:
            # 실패 시 기존 방식으로 대체
            writer = pd.ExcelWriter(output, engine='openpyxl')
            df.to_excel(writer, index=False)
            writer.save()
        
        output.seek(0)
        
        # 파일 전송
        filename = f"naver_news_{search_keyword}.xlsx"
        
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({"error": f"파일 다운로드 중 오류가 발생했습니다: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)