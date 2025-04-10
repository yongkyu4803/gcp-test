import streamlit as st
import pandas as pd
import time
import os
import base64
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 앱 설정
st.set_page_config(
    page_title="네이버 뉴스 크롤러",
    page_icon="📰",
    layout="wide"
)

# DataFrame을 다운로드 링크로 변환하는 함수
def get_download_link(df, filename, text):
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, engine='openpyxl')
    towrite.seek(0)
    b64 = base64.b64encode(towrite.read()).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx">{text}</a>'
    return href

# 네이버 뉴스 크롤링 함수
def crawl_naver_news(search_keyword, scroll_count, progress_bar, status_text):
    news_data = []
    
    # Chrome 옵션 설정
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # 웹드라이버 초기화
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # 네이버 뉴스 검색 페이지로 이동
        driver.get(f"https://search.naver.com/search.naver?where=news&sm=tab_jum&query={search_keyword}")
        
        # 스크롤 및 데이터 수집
        for i in range(scroll_count):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            progress_value = (i + 1) / scroll_count
            progress_bar.progress(progress_value)
            status_text.text(f"스크롤 {i+1}/{scroll_count} 완료")
            
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
        status_text.text(f"오류 발생: {str(e)}")
    
    finally:
        driver.quit()
    
    return news_data

# 메인 앱 함수
def main():
    st.title("네이버 뉴스 크롤러")
    st.markdown("네이버 뉴스 검색 결과를 크롤링하여 Excel 파일로 저장합니다.")
    
    # 사이드바 설정
    with st.sidebar:
        st.header("검색 설정")
        search_keyword = st.text_input("검색어를 입력하세요")
        scroll_count = st.slider("스크롤 횟수", min_value=1, max_value=20, value=5, 
                                help="더 많은 결과를 얻으려면 스크롤 횟수를 늘리세요")
        
        start_button = st.button("크롤링 시작", disabled=not search_keyword)
    
    # 메인 영역
    if not search_keyword:
        st.info("👈 사이드바에서 검색어를 입력하고 크롤링을 시작하세요.")
    
    # 크롤링 시작
    if start_button:
        st.subheader("크롤링 진행 상황")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("크롤링을 시작합니다...")
        
        # 크롤링 실행
        news_data = crawl_naver_news(search_keyword, scroll_count, progress_bar, status_text)
        
        # 결과 표시
        if not news_data:
            st.warning("검색 결과가 없습니다.")
        else:
            st.success(f"크롤링 완료! 총 {len(news_data)}개의 뉴스 기사를 찾았습니다.")
            
            # DataFrame 생성
            df = pd.DataFrame(news_data)
            
            # 엑셀 다운로드 링크
            excel_link = get_download_link(df, f"naver_news_{search_keyword}", "📥 Excel 파일 다운로드")
            st.markdown(excel_link, unsafe_allow_html=True)
            
            # 샘플 뉴스 표시
            st.subheader("샘플 뉴스")
            for i, news in enumerate(news_data[:3], 1):
                with st.expander(f"뉴스 {i}: {news['title']}"):
                    st.write(f"**언론사:** {news['press']}")
                    st.write(f"**시간:** {news['time']}")
                    if news['page_info']:
                        st.write(f"**지면 정보:** {news['page_info']}")
                    st.write(f"**내용:** {news['description']}")
                    st.write(f"**링크:** [{news['link']}]({news['link']})")
                    if news['naver_news_link']:
                        st.write(f"**네이버 뉴스 링크:** [{news['naver_news_link']}]({news['naver_news_link']})")
            
            # 전체 데이터 테이블 표시
            st.subheader("전체 데이터")
            st.dataframe(df)

if __name__ == "__main__":
    main()