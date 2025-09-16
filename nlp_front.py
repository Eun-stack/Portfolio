import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests

API_URL = "https://first.nstaaanp.store/analyze"

st.set_page_config(page_title="네덜란드어 의존 구문 분석기", layout="wide")
st.title("🇳🇱 네덜란드어 의존 구문 분석기")

user_input = st.text_area("네덜란드어 문장을 한 개만 입력하세요 (최대 300자).", max_chars=300)

if st.button("분석"):
    # 빈 값 체크
    if len(user_input.strip()) == 0:
        st.error("문장을 입력해주세요.")
    # 길이 체크 (max_chars가 막아주지만 혹시나 대비)
    elif len(user_input) > 300:
        st.error("300자 이하로 입력해주세요.")
    else:
        with st.spinner("분석 중..."):
            try:
                resp = requests.post(API_URL, json={"text": user_input}, timeout=10)
                if resp.status_code == 200:
                    result = resp.json()
                    sentence = result["sentence"]
                    word_list = result["word_list"]
                    sentence_data = result["sentence_data"]
                    arcs = result["arcs"]

                    st.subheader(f"📝 문장: {sentence}")
                    df = pd.DataFrame(sentence_data)
                    df.index = df.index + 1
                    st.dataframe(df)
                else:
                    st.error("분석 중 문제가 발생했습니다. 잠시 후 다시 시도해 주세요.")
            except requests.exceptions.Timeout:
                st.error("오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
            except requests.exceptions.ConnectionError:
                st.error("서버에 연결할 수 없습니다.")
            except Exception:
                st.error("오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")

            # ===== 시각화 =====
            try:
                if arcs:
                    st.markdown("🎯 **의존 구문 시각화**")
                    base_colors = plt.get_cmap('tab20').colors
                    extra_colors = [
                        (0.9, 0.1, 0.1), (0.1, 0.9, 0.1), (0.1, 0.1, 0.9),
                        (0.9, 0.5, 0.1), (0.5, 0.1, 0.9), (0.1, 0.9, 0.5),
                        (0.6, 0.2, 0.2), (0.2, 0.6, 0.2), (0.2, 0.2, 0.6),
                        (0.8, 0.3, 0.4)
                    ]
                    colors_30 = list(base_colors) + extra_colors

                    def get_color_by_distance(dist, colors=colors_30):
                        if dist < 1:
                            dist = 1
                        if dist > len(colors):
                            dist = len(colors)
                        return colors[dist - 1]

                    fig, ax = plt.subplots(figsize=(len(word_list) * 2.0, 3))
                    if len(word_list) > 15:
                        fig, ax = plt.subplots(figsize=(len(word_list) * 2.0, 6))

                    positions = list(range(len(word_list)))
                    ax.set_xticks(positions)
                    ax.set_xticklabels(word_list, fontsize=14)
                    ax.set_yticks([])
                    ax.set_ylim(0, max(4, max(abs(dep - head) for head, dep in arcs) + 1))
                    ax.set_xlim(-1, len(word_list))

                    for head, dep in arcs:
                        x_vals = np.linspace(min(head, dep), max(head, dep), 500)
                        amplitude = abs(dep - head)
                        if amplitude == 0:
                            amplitude = 1
                        height = amplitude * np.abs(np.sin(np.pi * (x_vals - min(head, dep)) / (max(head, dep) - min(head, dep))))
                        color = 'red' if df.loc[head+1, "의존관계코드"] == "root" else get_color_by_distance(amplitude)
                        linestyle = '--' if head < dep else '-'
                        ax.plot(x_vals, height, color=color, linestyle=linestyle, linewidth=2)

                    ax.set_title("Dependency Structure", fontsize=16)
                    st.pyplot(fig)
                    st.markdown("""
                    **범례**  
                    - 실선 : 왼쪽   → 오른쪽  
                    - 점선 : 오른쪽 → 왼쪽  
                    - ROOT에 의존한 단어는 빨간색 선
                    """)
                else:
                    st.error("오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
            except Exception:
                st.error("오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")

