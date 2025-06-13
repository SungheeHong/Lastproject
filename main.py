import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import re

# 🎯 유튜브 영상 ID 추출
def extract_video_id(url):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

# 🎯 자막(가사) 가져오기
def get_transcript_lines(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        # 각 entry['text']를 한 줄로 취급
        return [entry["text"] for entry in transcript]
    except (TranscriptsDisabled, NoTranscriptFound):
        return None

# 🎯 한 페이지당 최대 3줄로 분할
def paginate_lines(lines, lines_per_page=3):
    pages = []
    for i in range(0, len(lines), lines_per_page):
        pages.append(lines[i : i + lines_per_page])
    return pages

# ─── Streamlit 앱 시작 ──────────────────────────────────────────
st.set_page_config(page_title="🎵 유튜브 가사 뷰어", layout="centered")
st.title("🎶 유튜브 노래 가사 뷰어")
st.write("유튜브 URL을 넣으면 노래 가사를 한 페이지에 3줄씩 보여줘!")

url = st.text_input("🔗 유튜브 영상 URL 입력")

if url:
    vid = extract_video_id(url)
    if not vid:
        st.error("❌ 유효한 유튜브 링크가 아니야!")
    else:
        with st.spinner("⏳ 가사(자막) 불러오는 중..."):
            lines = get_transcript_lines(vid)

        if lines is None:
            st.error("⚠️ 이 영상은 자막이 없거나 사용할 수 없어.")
        else:
            pages = paginate_lines(lines, lines_per_page=3)
            # 세션 상태에 현재 페이지 저장
            if "page" not in st.session_state:
                st.session_state.page = 0

            st.subheader(f"페이지 {st.session_state.page + 1} / {len(pages)}")
            # 가사 3줄 표시
            for line in pages[st.session_state.page]:
                st.markdown(f"<p style='font-size:20px; line-height:1.4'>{line}</p>", unsafe_allow_html=True)

            # 이전/다음 버튼
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("⬅️ 이전") and st.session_state.page > 0:
                    st.session_state.page -= 1
            with col3:
                if st.button("다음 ➡️") and st.session_state.page < len(pages) - 1:
                    st.session_state.page += 1

