import feedparser
import os
import smtplib
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai
from datetime import datetime

# --- 설정(Configuration) ---
GOOGLE_NEWS_URL = "https://news.google.com/rss/search?q={}&hl=ko&gl=KR&ceid=KR:ko"
KEYWORDS = ["IT아웃소싱", "MSP", "클라우드 운영전환", "LG CNS", "SK AX", "베트남 개발자"]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") 
EMAIL_RECEIVER = "본인이메일@gmail.com" # ★여기에 메일을 받을 주소를 다시 적어주세요!★

client = genai.Client(api_key=GEMINI_API_KEY)

def get_news(keywords):
    news_list = []
    for keyword in keywords:
        encoded_keyword = urllib.parse.quote(keyword)
        feed = feedparser.parse(GOOGLE_NEWS_URL.format(encoded_keyword))
        for entry in feed.entries[:3]:
            news_list.append({"title": entry.title, "link": entry.link})
    return news_list

def generate_insights(news_list):
    news_text = "\n".join([f"- {news['title']} ({news['link']})" for news in news_list])
    
    # 프롬프트를 첨부하신 이미지 디자인에 맞게 완전히 수정했습니다.
    prompt = f"""
    당신은 GDC 사업 담당자입니다. 다음 수집된 기사들을 분석하여 아래 2가지 섹션의 HTML 코드를 작성해주세요.
    반드시 제공된 HTML 태그와 인라인 CSS 형식만 사용하여 출력하세요. 마크다운(```html 등)은 절대 포함하지 마세요.

    <h3 style="font-size: 16px; margin-bottom: 10px;">📊 1. GDC & ITO 트렌드 매트릭스 (Market vs Competitor)</h3>
    <table style="width: 100%; border-collapse: collapse; font-size: 13px; margin-bottom: 30px;">
        <thead>
            <tr>
                <th style="border: 1px solid #ddd; background-color: #f4f6f9; padding: 10px; text-align: center; width: 15%;">구분</th>
                <th style="border: 1px solid #ddd; background-color: #eef2f5; padding: 10px; text-align: left; width: 42.5%;">🇰🇷 국내 시장 (Domestic)</th>
                <th style="border: 1px solid #ddd; background-color: #eef2f5; padding: 10px; text-align: left; width: 42.5%;">🌎 글로벌 시장 (International)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: bold; background-color: #fafafa;">시장 전반<br><span style="font-size: 11px; font-weight: normal; color: #666;">(Market & IT)</span></td>
                <td style="border: 1px solid #ddd; padding: 10px;">(이곳에 뉴스 데이터 기반 국내 시장 동향을 링크 포함 작성)</td>
                <td style="border: 1px solid #ddd; padding: 10px;">(이곳에 뉴스 데이터 기반 글로벌 시장 동향을 링크 포함 작성)</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: bold; background-color: #fafafa;">경쟁사 동향<br><span style="font-size: 11px; font-weight: normal; color: #666;">(Competitors)</span></td>
                <td style="border: 1px solid #ddd; padding: 10px;">(이곳에 뉴스 데이터 기반 국내 경쟁사 동향을 링크 포함 작성)</td>
                <td style="border: 1px solid #ddd; padding: 10px;">(이곳에 뉴스 데이터 기반 글로벌 경쟁사 동향을 링크 포함 작성)</td>
            </tr>
        </tbody>
    </table>

    <h3 style="font-size: 16px; margin-bottom: 10px;">💡 2. GDC 비즈니스 시사점 (Insights)</h3>
    <ol style="font-size: 14px; padding-left: 20px; line-height: 1.6; margin-bottom: 30px;">
        <li style="margin-bottom: 15px;">
            <b>[시사점 1 제목]</b>
            <ul style="list-style-type: circle; padding-left: 20px; margin-top: 5px;">
                <li><b>배경:</b> [내용]</li>
                <li><b>GDC 전략:</b> [내용]</li>
                <li><b>🔗 뒷받침 뉴스:</b> <a href="[링크]" style="color: #0056b3; text-decoration: none;">[기사제목]</a></li>
            </ul>
        </li>
        <li style="margin-bottom: 15px;">
            <b>[시사점 2 제목]</b>
            <ul style="list-style-type: circle; padding-left: 20px; margin-top: 5px;">
                <li><b>배경:</b> [내용]</li>
                <li><b>GDC 전략:</b> [내용]</li>
                <li><b>🔗 뒷받침 뉴스:</b> <a href="[링크]" style="color: #0056b3; text-decoration: none;">[기사제목]</a></li>
            </ul>
        </li>
        <li style="margin-bottom: 15px;">
            <b>[시사점 3 제목]</b>
            <ul style="list-style-type: circle; padding-left: 20px; margin-top: 5px;">
                <li><b>배경:</b> [내용]</li>
                <li><b>GDC 전략:</b> [내용]</li>
                <li><b>🔗 뒷받침 뉴스:</b> <a href="[링크]" style="color: #0056b3; text-decoration: none;">[기사제목]</a></li>
            </ul>
        </li>
    </ol>

    뉴스 데이터:
    {news_text}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    # AI가 혹시 마크다운(```html)을 붙여서 출력하면 이를 제거합니다.
    clean_html = response.text.replace("```html", "").replace("```", "").strip()
    return clean_html

def send_email(insights_html):
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 전체 메일 컨테이너 스타일링 (이미지 시안과 동일한 폰트 및 여백)
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; color: #333; line-height: 1.5; padding: 20px; max-width: 900px; margin: 0 auto;">
        
        <h2 style="font-size: 20px; border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px;">
            📄 GDC & ITO 트렌드 뉴스레터 ({today})
        </h2>
        
        {insights_html}
        
        <h3 style="font-size: 16px; margin-bottom: 10px;">🎯 3. 경쟁사 및 외국인 IT 인력 채용 동향</h3>
        <ul style="font-size: 13px; list-style-type: circle; padding-left: 20px; line-height: 1.8;">
            <li><b>SK AX:</b> <a href="#" style="color: #0056b3; text-decoration: none;">글로벌 사업 파트 - 베트남 거점 BSE (Bridge Software Engineer) 채용 (경력 3년 이상) ~6/15</a></li>
            <li><b>LG CNS:</b> <a href="#" style="color: #0056b3; text-decoration: none;">클라우드/MSP 아키텍트 (외국인 지원 가능/F-2, F-5 비자 우대) ~상시</a></li>
            <li><b>FPT Korea:</b> <a href="#" style="color: #0056b3; text-decoration: none;">한국 엔터프라이즈 영업 담당자 (베트남어 능통자 우대) ~6/10</a></li>
            <li><b>Sotatek:</b> <a href="#" style="color: #0056b3; text-decoration: none;">Web3/AI 프로젝트 리딩용 한국인 PM/PL 영입 ~채용시 마감</a></li>
            <li><b>국내 스타트업 (A사):</b> <a href="#" style="color: #0056b3; text-decoration: none;">사내 GDC 구축을 위한 베트남 개발팀 리드 (한국 거주자) ~6/30</a></li>
        </ul>
        
    </body>
    </html>
    """
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"[Daily GDC Insight] 글로벌/국내 ITO 트렌드 리포트 ({today})"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg.attach(MIMEText(html_content, 'html'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

if __name__ == "__main__":
    news_data = get_news(KEYWORDS)
    insights = generate_insights(news_data)
    send_email(insights) # 이제 뉴스 원본 목록은 AI가 매트릭스로 정리하므로 제외합니다.
