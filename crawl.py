import os, requests
from datetime import datetime

CLIENT_ID = os.environ["NAVER_CLIENT_ID"]
CLIENT_SECRET = os.environ["NAVER_CLIENT_SECRET"]

SPORTS_KEYWORDS = ["야구","축구","농구","배구","골프","스포츠","선수","경기","리그","올림픽"]

def is_sports(title, desc):
    text = title + desc
    return any(kw in text for kw in SPORTS_KEYWORDS)

def fetch_news():
    url = "https://openapi.naver.com/v1/search/news.json"
    headers = {"X-Naver-Client-Id": CLIENT_ID, "X-Naver-Client-Secret": CLIENT_SECRET}
    params = {"query": "삼성생명", "display": 50, "sort": "date"}
    res = requests.get(url, headers=headers, params=params)
    items = res.json().get("items", [])
    filtered = []
    for item in items:
        title = item["title"].replace("<b>","").replace("</b>","")
        desc = item["description"].replace("<b>","").replace("</b>","")
        if not is_sports(title, desc):
            filtered.append({
                "title": title,
                "link": item["originallink"],
                "desc": desc,
                "date": item["pubDate"]
            })
    return filtered

def build_html(articles):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    rows = ""
    for a in articles:
        rows += f"""
        <tr>
          <td><a href="{a['link']}" target="_blank">{a['title']}</a></td>
          <td>{a['desc'][:80]}...</td>
          <td>{a['date']}</td>
        </tr>"""
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>삼성생명 뉴스</title>
  <style>
    body {{ font-family: sans-serif; max-width: 1000px; margin: 40px auto; padding: 0 20px; }}
    h1 {{ color: #003087; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ background: #003087; color: white; padding: 10px; }}
    td {{ padding: 10px; border-bottom: 1px solid #ddd; vertical-align: top; }}
    a {{ color: #003087; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <h1>📰 삼성생명 뉴스 게시판</h1>
  <p>기준일: {today} | 총 {len(articles)}건 (스포츠 제외)</p>
  <table>
    <tr><th>제목</th><th>내용 요약</th><th>날짜</th></tr>
    {rows}
  </table>
</body>
</html>"""

news = fetch_news()
html = build_html(news)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"완료: {len(news)}건")
