import streamlit as st
from datetime import datetime
from collections import Counter
import csv
import re
import io
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

st.set_page_config(page_title="NOS RSS crawler", layout="wide")
st.title("NOS RSS crawler & trefwoorden")

# --------------------- Disclaimer ---------------------
st.info(
    """
    이 앱은 **NOS의 공식 RSS 피드**만 사용합니다. 본문 전문을 저장/배포하지 않으며,
    화면에는 **짧은 요약(최대 3문장·500자)** 만 표시합니다. 모든 저작권은 원 출처(NOS.nl)에 있습니다.
    """,
    icon="ℹ️",
)

# --------------------- Stopwoorden ---------------------
dutch_stopwords = {
    "de", "en", "van", "ik", "te", "dat", "die", "in", "een", "hij", "het", "niet",
    "zijn", "is", "was", "op", "aan", "met", "als", "voor", "had", "er", "maar",
    "om", "hem", "dan", "zou", "of", "wat", "mijn", "men", "dit", "zo", "door",
    "over", "ze", "zich", "bij", "ook", "tot", "je", "mij", "uit", "der", "daar",
    "haar", "naar", "heb", "hoe", "heeft", "hebben", "deze", "u", "want", "nog",
    "zal", "me", "zij", "nu", "ge", "geen", "omdat", "iets", "worden", "toch",
    "al", "waren", "veel", "meer", "doen", "toen", "모et", "ben", "zonder", "kan",
    "hun", "dus", "alles", "onder", "ja", "werd", "wezen", "zelf", "tegen",
    "komen", "goed", "hier", "wie", "waarom"
}

# --------------------- Helper: safe preview ---------------------
def make_safe_preview(md_text: str, max_sentences: int = 3, max_chars: int = 500) -> str:
    if not md_text:
        return ""
    text = re.sub(r"\s+", " ", md_text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    preview = " ".join(sentences[:max_sentences]).strip()
    if len(preview) > max_chars:
        cut = preview[:max_chars]
        if " " in cut:
            cut = cut.rsplit(" ", 1)[0]
        preview = cut.rstrip(" .,;:") + "…"
    return preview

# --------------------- Trefwoordenextractie ---------------------
def extract_keywords(text: str, top_n: int = 10):
    words = re.findall(r"\b[a-zA-Z]{8,}\b", text)
    capitalized_words = [w.capitalize() for w in words]
    filtered_words = [w for w in capitalized_words if w.lower() not in dutch_stopwords]
    freq = Counter(filtered_words)

    unique_keywords = []
    for word, _ in freq.most_common():
        if word not in unique_keywords:
            unique_keywords.append(word)
        if len(unique_keywords) >= top_n:
            break

    return [(kw, freq[kw]) for kw in unique_keywords], filtered_words

# --------------------- HTML to text ---------------------
def html_to_text(html: str) -> str:
    soup = BeautifulSoup(html or "", "html.parser")
    return soup.get_text(separator=" ", strip=True)

# --------------------- RSS Fetch (표준 XML로) ---------------------
def fetch_rss_items(feed_url: str, count: int = 5, progress_bar=None):
    try:
        resp = requests.get(feed_url, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        st.error(f"RSS 피드 요청 실패: {e}")
        return []

    # RSS 피드 파싱 (ElementTree)
    try:
        tree = ET.fromstring(resp.content)
    except Exception as e:
        st.error(f"RSS XML 파싱 실패: {e}")
        return []

    # RSS 2.0: <item>들, Atom일 경우 <entry>들
    items = tree.findall(".//item")
    if not items:
        # Atom 지원
        items = tree.findall(".//{http://www.w3.org/2005/Atom}entry")
        atom = True
    else:
        atom = False

    total = min(count, len(items))
    out = []

    for i, item in enumerate(items[:total], start=1):
        if atom:
            get = lambda tag: item.find(f"{{http://www.w3.org/2005/Atom}}{tag}")
            title = get("title").text if get("title") is not None else "(geen titel)"
            link = None
            for l in item.findall(f"{{http://www.w3.org/2005/Atom}}link"):
                if l.attrib.get("type") == "text/html" or l.attrib.get("rel") == "alternate":
                    link = l.attrib.get("href")
                    break
            link = link or (get("link").attrib.get("href") if get("link") is not None else "")
            summary_html = get("summary").text if get("summary") is not None else ""
        else:
            get = lambda tag: item.find(tag)
            title = get("title").text if get("title") is not None else "(geen titel)"
            link = get("link").text if get("link") is not None else ""
            summary_html = get("description").text if get("description") is not None else ""

        summary_txt = html_to_text(summary_html)
        keywords, _ = extract_keywords(f"{title}\n{summary_txt}")

        out.append({
            "title": title,
            "url": link,
            "summary": summary_txt,
            "keywords": [kw for kw, _ in keywords],
        })

        if progress_bar:
            progress_bar.progress(int(i / max(total, 1) * 100))

    if progress_bar:
        progress_bar.empty()

    return out

# --------------------- CSV ---------------------
def generate_csv_bytes(result):
    if not result:
        return None
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["index", "title", "url", "keywords"])
    writer.writeheader()
    for idx, item in enumerate(result, 1):
        writer.writerow({
            "index": idx,
            "title": item["title"],
            "url": item["url"],
            "keywords": ", ".join(item["keywords"]),
        })
    return output.getvalue().encode("utf-8-sig")

# --------------------- UI ---------------------
presets = {
    "NOS Nieuws Algemeen": "https://feeds.nos.nl/nosnieuwsalgemeen",
    "NOS Binnenland": "https://feeds.nos.nl/nosnieuwsbinnenland",
    "NOS Buitenland": "https://feeds.nos.nl/nosnieuwsbuitenland",
    "NOS Politiek": "https://feeds.nos.nl/nosnieuwspolitiek",
    "NOS Economie": "https://feeds.nos.nl/nosnieuwseconomie",
    "NOS Tech": "https://feeds.nos.nl/nosnieuwstech",
    "NOS Opmerkelijk": "https://feeds.nos.nl/nosnieuwsopmerkelijk",
    "NOS Sport Algemeen": "https://feeds.nos.nl/nossportalgemeen",
}

left, right = st.columns([2, 3])
with left:
    preset_name = st.selectbox("RSS 프리셋 선택", list(presets.keys()) + ["Custom"])

with right:
    default_url = presets.get(preset_name, "https://feeds.nos.nl/nosnieuwsalgemeen")
    feed_url = st.text_input("또는 RSS URL 직접 입력", value=default_url, help="매체의 공식 RSS URL을 입력하세요.")

article_count = st.slider("항목 수", 1, 20, 5)

# --------------------- Start Crawling ---------------------
if st.button("RSS 가져오기"):
    progress = st.progress(0)
    result = fetch_rss_items(feed_url, article_count, progress)
    if result:
        st.session_state["rss_result"] = result
        st.success(f"✅ {len(result)}개의 뉴스 항목을 가져왔습니다.")

# --------------------- Show Results ---------------------
if "rss_result" in st.session_state:
    result = st.session_state["rss_result"]

    for i, item in enumerate(result, 1):
        st.markdown(f"### {i}. {item['title']}")
        st.markdown(f"🔗 [원문 링크]({item['url']})")
        st.markdown(f"**Trefwoorden:** {', '.join(item['keywords'])}")
        with st.expander("요약 보기 (최대 3문장·500자)"):
            preview = make_safe_preview(item["summary"])
            st.markdown(preview or "(요약 없음)")
            if item["url"]:
                st.markdown(f"_Bron: [NOS.nl]({item['url']})_")

    if st.button("📥 CSV 저장하기"):
        csv_bytes = generate_csv_bytes(result)
        if csv_bytes:
            st.session_state["csv_data"] = csv_bytes
            st.success("✅ CSV 파일이 생성되었습니다.")
        else:
            st.warning("⚠️ 저장할 데이터가 없습니다.")

    if "csv_data" in st.session_state:
        st.download_button(
            label="📄 CSV 다운로드",
            data=st.session_state["csv_data"],
            file_name=f"nos_rss_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
        )
