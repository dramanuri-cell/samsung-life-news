import os, requests, re
from datetime import datetime

CLIENT_ID = os.environ["NAVER_CLIENT_ID"]
CLIENT_SECRET = os.environ["NAVER_CLIENT_SECRET"]

SPORTS_KEYWORDS = ["야구","축구","농구","배구","골프","스포츠","선수","경기","리그","올림픽"]

def is_sports(title, desc):
    text = title + desc
    return any(kw in text for kw in SPORTS_KEYWORDS)

def extract_publisher(url):
    patterns = {
        "chosun.com": "조선일보", "joongang.co.kr": "중앙일보",
        "donga.com": "동아일보", "hani.co.kr": "한겨레",
        "kmib.co.kr": "국민일보", "segye.com": "세계일보",
        "munhwa.com": "문화일보", "seoul.co.kr": "서울신문",
        "hankyung.com": "한국경제", "mk.co.kr": "매일경제",
        "etnews.com": "전자신문", "zdnet.co.kr": "지디넷",
        "yonhapnews.co.kr": "연합뉴스", "yna.co.kr": "연합뉴스",
        "newsis.com": "뉴시스", "news1.kr": "뉴스1",
        "edaily.co.kr": "이데일리", "mt.co.kr": "머니투데이",
        "thebell.co.kr": "더벨", "inews24.com": "아이뉴스24",
        "heraldcorp.com": "헤럴드경제", "sedaily.com": "서울경제",
        "fnnews.com": "파이낸셜뉴스", "ajunews.com": "아주경제",
    }
    for domain, name in patterns.items():
        if domain in url:
            return name
    match = re.search(r'https?://(?:www\.)?([^/]+)', url)
    return match.group(1) if match else "기타"

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
        link = item["originallink"]
        if not is_sports(title, desc):
            filtered.append({
                "title": title,
                "link": link,
                "desc": desc,
                "date": item["pubDate"],
                "publisher": extract_publisher(link)
            })
    filtered.sort(key=lambda x: x["date"], reverse=True)
    return filtered

def build_html(articles):
    today = datetime.now().strftime("%Y년 %m월 %d일")
    rows = ""
    for a in articles:
        rows += f"""
        <tr>
          <td>{a['date'][:16]}</td>
          <td>{a['publisher']}</td>
          <td><a href="{a['link']}" target="_blank">{a['title']}</a></td>
          <td>{a['desc'][:80]}...</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>삼성생명 뉴스</title>
  <style>
    body {{ font-family: sans-serif; max-width: 1100px; margin: 40px auto; padding: 0 20px; }}
    h1 {{ color: #003087; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th {{ background: #003087; color: white; padding: 10px; text-align: left; }}
    td {{ padding: 10px; border-bottom: 1px solid #ddd; vertical-align: top; }}
    td:nth-child(2) {{ white-space: nowrap; color: #666; font-size: 13px; }}
    a {{ color: #003087; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .btn {{ background: #003087; color: white; border: none; padding: 10px 20px;
            font-size: 15px; border-radius: 6px; cursor: pointer; margin-bottom: 20px; }}
    @media print {{ .btn {{ display: none; }} }}
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
</head>
<body>
  <h1>📰 삼성생명 뉴스 게시판</h1>
  <p>기준일: {today} | 총 {len(articles)}건 (스포츠 제외)</p>
  <button class="btn" onclick="downloadPDF()">📥 PDF 다운로드</button>
  <table id="news-table">
    <tr><th>날짜</th><th>언론사</th><th>제목</th><th>내용 요약</th></tr>
    {rows}
  </table>
  <script>
    function downloadPDF() {{
      const el = document.getElementById('news-table');
      const opt = {{
        margin: 10,
        filename: '삼성생명뉴스_{today}.pdf',
        image: {{ type: 'jpeg', quality: 0.98 }},
        html2canvas: {{ scale: 2 }},
        jsPDF: {{ unit: 'mm', format: 'a4', orientation: 'landscape' }}
      }};
      html2pdf().set(opt).from(el).save();
    }}
  </script>
</body>
</html>"""

news = fetch_news()
html = build_html(news)
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
print(f"완료: {len(news)}건")
