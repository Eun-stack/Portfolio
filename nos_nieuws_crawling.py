import streamlit as st
from datetime import datetime
from collections import Counter
import csv
import re
import io
import feedparser
import html2text

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
    """RSS 요약 반환
    - 문장 기준 최대 3문장
    - 총 길이 최대 500자
    """
    if not md_text:
        return ""
    # 공백 정리
    text = re.sub(r"\s+", " ", md_text).strip()
    # 단순 문장 분리 (., !, ? 뒤 공백 기준) — 네덜란드어 포함 일반적 케이스 커버
    sentences = re.split(r"(?<=[.!?])\s+", text)
    preview = " ".join(sentences[:max_sentences]).strip()
    # 글자 수 제한
    if len(preview) > max_chars:
        cut = preview[:max_chars]
        # 마지막 단어 경계에서 자르기
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

# --------------------- RSS Fetch ---------------------
def fetch_rss_items(feed_url: str, count: int = 5, progress_bar=None):
    parsed = feedparser.parse(feed_url)
    entries = parsed.entries or []

    total = min(count, len(entries)) if entries else 0
    out = []
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.body_width = 0

    for i, e in enumerate(entries[:total], start=1):
        title = getattr(e, "title", "(geen titel)")
        link = getattr(e, "link", "")
        summary_html = getattr(e, "summary", getattr(e, "description", ""))
        summary_md = h.handle(summary_html).strip()

        keywords, _ = extract_keywords(f"{title}\n{summary_md}")

        out.append({
            "title": title,
            "url": link,
            "summary": summary_md,  # 원본 요약(전체) — 화면표시는 make_safe_preview로 제한
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
            preview = make_safe_preview(item["summary"])  # 항상 짧게 제한된 요약만 노출
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
