$(document).ready(function() {
    // 전역 변수
    let newsData = [];
    let searchKeyword = '';
    
    // 스크롤 값 표시
    $('#scroll_count').on('input', function() {
        $('#scroll_value').text($(this).val());
    });
    
    // 검색어 입력 시 버튼 활성화
    $('#search_keyword').on('input', function() {
        $('#start_crawl').prop('disabled', $(this).val().trim() === '');
    });
    
    // 크롤링 시작 버튼 클릭
    $('#start_crawl').click(function() {
        searchKeyword = $('#search_keyword').val().trim();
        const scrollCount = $('#scroll_count').val();
        
        if (!searchKeyword) {
            alert('검색어를 입력해주세요.');
            return;
        }
        
        // UI 초기화
        $('#initial_message').addClass('d-none');
        $('#results').addClass('d-none');
        $('#crawling_progress').removeClass('d-none');
        $('#progress_bar').css('width', '0%');
        $('#status_text').text('크롤링을 시작합니다...');
        
        // 크롤링 요청
        $.ajax({
            url: window.location.origin + '/crawl',  // 절대 경로로 변경
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                search_keyword: searchKeyword,
                scroll_count: scrollCount
            }),
            beforeSend: function() {
                // 진행 상황 시뮬레이션
                let progress = 0;
                const interval = setInterval(function() {
                    progress += 5;
                    if (progress > 90) {
                        clearInterval(interval);
                        return;
                    }
                    $('#progress_bar').css('width', progress + '%');
                    $('#status_text').text(`크롤링 진행 중... ${progress}%`);
                }, scrollCount * 200);
                
                // 요청 완료 시 인터벌 제거를 위해 저장
                $(this).data('interval', interval);
            },
            success: function(response) {
                clearInterval($(this).data('interval'));
                $('#progress_bar').css('width', '100%');
                $('#status_text').text('크롤링 완료!');
                
                // 데이터 저장
                newsData = response.data;
                
                // 결과 표시
                showResults(response);
            },
            error: function(xhr) {
                clearInterval($(this).data('interval'));
                $('#progress_bar').css('width', '100%');
                
                let errorMsg = '크롤링 중 오류가 발생했습니다.';
                if (xhr.responseJSON && xhr.responseJSON.error) {
                    errorMsg = xhr.responseJSON.error;
                }
                
                $('#status_text').text(errorMsg);
                alert(errorMsg);
            },
            complete: function() {
                setTimeout(function() {
                    $('#crawling_progress').addClass('d-none');
                }, 1000);
            }
        });
    });
    
    // 엑셀 다운로드 버튼 클릭
    $('#download_excel').click(function() {
        if (newsData.length === 0) {
            alert('다운로드할 데이터가 없습니다.');
            return;
        }
        
        // 다운로드 요청
        fetch(window.location.origin + '/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                news_data: newsData,
                search_keyword: searchKeyword
            }),
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `naver_news_${searchKeyword}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            console.error('다운로드 중 오류 발생:', error);
            alert('파일 다운로드 중 오류가 발생했습니다.');
        });
    });
    
    // 결과 표시 함수
    function showResults(response) {
        $('#results').removeClass('d-none');
        $('#success_message').text(`크롤링 완료! 총 ${response.count}개의 뉴스 기사를 찾았습니다.`);
        
        // 샘플 뉴스 표시
        const sampleNews = $('#sample_news');
        sampleNews.empty();
        
        response.sample.forEach((news, index) => {
            const card = $(`
                <div class="card news-card mb-3">
                    <div class="card-header">
                        <h5 class="mb-0">${news.title}</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>${news.press} / 시간: ${news.time}</strong></p>
                        <p>${news.description}</p>
                        <p><a href="${news.link}" target="_blank">${news.link}</a></p>
                        ${news.naver_news_link ? `<p><strong>네이버 뉴스 링크:</strong> <a href="${news.naver_news_link}" target="_blank">${news.naver_news_link}</a></p>` : ''}
                    </div>
                </div>
            `);
            
            sampleNews.append(card);
        });
        
        // 테이블 데이터 표시
        const tableBody = $('#news_table tbody');
        tableBody.empty();
        
        response.data.forEach(news => {
            const row = $(`
                <tr>
                    <td>${news.title}</td>
                    <td>${news.press}</td>
                    <td>${news.time}</td>
                    <td>${news.description.substring(0, 100)}${news.description.length > 100 ? '...' : ''}</td>
                    <td><a href="${news.link}" target="_blank">링크</a></td>
                </tr>
            `);
            
            tableBody.append(row);
        });
    }
});