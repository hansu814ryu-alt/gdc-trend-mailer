import feedparser
import os
import smtplib
import urllib.parse  # 띄어쓰기 변환을 위한 도구 추가
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai  # 최신 구글 AI 패키지로 변경
from datetime import datetime

GOOGLE_NEWS_URL = "https://news.google.com/rss/search?q={}&hl=ko&gl=KR&ceid=KR:ko"
KEYWORDS = ["IT아웃소싱", "MSP", "클라우드 운영전환", "LG CNS", "SK AX", "베트남 개발자"]

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") 

# ★여기에 메일을 받을 분의 이메일 주소를 직접 적어주세요!★
EMAIL_RECEIVER = "hansu814.ryu@samsung.com"

# 최신 Gemini Client 초기화
client = genai.Client(api_key=GEMINI_API_KEY)

def get_news(keywords):
    news_list = []
    for keyword in keywords:
        # 키워드에 띄어쓰기가 있어도 인터넷 주소용으로 안전하게 자동 변환
        encoded_keyword = urllib.parse.quote(keyword)
        feed = feedparser.parse(GOOGLE_NEWS_URL.format(encoded_keyword))
        for entry in feed.entries[:3]:
            news_list.append({"title": entry.title, "link": entry.link})
    return news_list

def generate_insights(news_list):
    news_text = "\n".join([f"- {news['title']} ({news['link']})" for news in news_list])
    prompt = f"""당신은 GDC 사업 담당자입니다. 다음 수집된 기사들을 분석하여 GDC 비즈니스 시사점 3가지를 HTML로 출력하세요: <p><b>1. [제목]</b></p> <ul><li><b>배경:</b> [내용]</li><li><b>🔗 뒷받침 뉴스:</b> <a href="[링크]">[기사제목]</a></li></ul> 뉴스 데이터: {news_text}"""
    
    # 최신 패키지에 맞춘 코드 호출 방식 변경
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )
    return response.text

def send_email(news_list, insights_html):
    today = datetime.now().strftime("%Y-%m-%d")
    html_content = f"<html><body><h2>🚀 [Daily] GDC & ITO 트렌드 ({today})</h2><h3>💡 시사점</h3>{insights_html}<br><h3>📰 수집 원본</h3><ul>"
    for news in news_list:
        html_content += f"<li><a href='{news['link']}'>{news['title']}</a></li>"
    html_content += "</ul></body></html>"
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"[Daily GDC Insight] ITO 트렌드 ({today})"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg.attach(MIMEText(html_content, 'html'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

if __name__ == "__main__":
    news_data = get_news(KEYWORDS)
    insights = generate_insights(news_data)
    send_email(news_data, insights)
