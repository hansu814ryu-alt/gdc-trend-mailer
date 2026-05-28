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
EMAIL_RECEIVER = "hansu814.ryu@samsung.com"

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
    
    # AI에게 링크 생성을 강제하는 엄격한 규칙을 추가했습니다.
    prompt = f"""
    당신은 GDC 사업 담당자입니다. 다음 수집된 기사들을 분석하여 아래 2가지 섹션의 HTML 코드를 작성해주세요.

    [🚨매우 중요한 링크 규칙🚨]
    매트릭스(표) 안의 내용과 하단의 '뒷받침 뉴스'에 들어가는 모든 기사 제목은 반드시 아래 예시처럼 클릭 가능한 HTML a 태그로 작성해야 합니다.
    올바른 예시: <a href="실제기사주소" target="_blank" style="color: #0056b3; text-decoration: underline;">기사 제목</a>
    절대 URL을 일반 텍스트나 괄호 형태로 그대로 노출하지 마세요.

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
                <td style="border: 1px solid #ddd; padding: 10px;">(뉴스 데이터를 바탕으로 a 태그 링크가 포함된 동향 작성)</td>
                <td style="border: 1px solid #ddd; padding: 10px;">(뉴스 데이터를 바탕으로 a 태그 링크가 포함된 동향 작성)</td>
            </tr>
            <tr>
                <td style="border: 1px solid #ddd; padding: 10px; text-align: center; font-weight: bold; background-color: #fafafa;">경쟁사 동향<br><span style="font-size: 11px; font-weight: normal; color: #666;">(Competitors)</span></td>
                <td style="border: 1px solid #ddd; padding: 10px;">(뉴스 데이터를 바탕으로 a 태그 링크가 포함된 동향 작성)</td>
                <td style="border: 1px solid #ddd; padding: 10px;">(뉴스 데이터를 바탕으로 a 태그 링크가 포함된 동향 작성)</td>
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
                <li><b>🔗 뒷받침 뉴스:</b> <a href="[링크]" style="color: #0056b3; text-decoration: underline;">[기사제목]</a></li>
            </ul>
        </li>
        <li style="margin-bottom: 15px;">
            <b>[시사점 2 제목]</b>
            <ul style="list-style-type: circle; padding-left: 20px; margin-top: 5px;">
                <li><b>배경:</b> [내용]</li>
                <li><b>GDC 전략:</b> [내용]</li>
                <li><b>🔗 뒷받침 뉴스:</b> <a href="[링크]" style="color: #0056b3; text-decoration: underline;">[기사제목]</a></li>
            </ul>
        </li>
        <li style="margin-bottom: 15px;">
            <b>[시사점 3 제목]</b>
            <ul style="list-style-type: circle; padding-left: 20px; margin-top: 5px;">
                <li><b>배경:</b> [내용]</li>
                <li><b>GDC 전략:</b> [내용]</li>
                <li><b>🔗 뒷받침 뉴스:</b> <a href="[링크]" style="color: #0056b3; text-decoration: underline;">[기사제목]</a></li>
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
    clean_html = response.text.replace("```html", "").replace("```", "").strip()
    return clean_html

def send_email(insights_html):
    today = datetime.now().strftime("%Y-%m-%d")
    
    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
    </head>
    <body style="font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; color: #333; line-height: 1.5; padding: 20px; max-width: 900px; margin: 0 auto;">
        
        <h2 style="font-size: 20px; border-bottom: 2px solid #333; padding-bottom
