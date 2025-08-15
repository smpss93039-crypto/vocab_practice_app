import streamlit as st
import pandas as pd
import random
import requests
import io

# ====== Google Fonts & CSS ======
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Times+New+Roman&display=swap');

    html, body, [class*="css"] {
        font-family: "宋体", "SimSun", "Times New Roman", serif;
    }

    .title-box {
        border: 2px solid #444;
        padding: 10px;
        font-size: 24px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 15px;
    }
    .word {
        font-size: 36px;
        font-weight: bold;
        font-family: "Times New Roman", serif;
        margin-bottom: 5px;
    }
    .phonetic {
        font-size: 20px;
        color: gray;
        font-family: "Times New Roman", serif;
        margin-bottom: 10px;
    }
    .example {
        font-size: 28px;
        color: #444;
        font-family: "宋体", "SimSun", serif;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ====== Google Sheet 設定 ======
SHEET_ID = "1fu6Lm3J54fo-hYOXmoYwHtylNSKIH8rDd6Syvpc9wuA"

def get_csv_url(sheet_name):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

@st.cache_data
def load_data(sheet_name):
    CSV_URL = get_csv_url(sheet_name)
    r = requests.get(CSV_URL)
    r.encoding = 'utf-8-sig'
    df = pd.read_csv(io.StringIO(r.text))
    return df

# ====== 初始化 session state ======
if "user" not in st.session_state:
    st.session_state.user = None
if "question" not in st.session_state:
    st.session_state.question = None
    st.session_state.correct = None
    st.session_state.phonetic = ""
    st.session_state.example = ""
    st.session_state.used_indices = set()
    st.session_state.show_answer = False  # 是否顯示答案
    st.session_state.input_text = ""      # 使用者輸入

# ====== 選擇使用者 ======
def select_user(user_name):
    st.session_state.user = user_name
    st.session_state.data = load_data(user_name)
    st.session_state.used_indices = set()
    new_question()

# ====== 產生新題目（不重複） ======
def new_question():
    df = st.session_state.data
    available_indices = set(df.index) - st.session_state.used_indices
    if not available_indices:
        st.success("已完成所有題目！")
        return
    idx = random.choice(list(available_indices))
    st.session_state.used_indices.add(idx)

    row = df.loc[idx]
    st.session_state.question = row["english"]
    st.session_state.phonetic = row.get("phonetic", "")
    st.session_state.example = row.get("example", "")
    st.session_state.correct = row["chinese"]

    st.session_state.show_answer = False
    st.session_state.input_text = ""

# ====== 按下確認按鍵的邏輯 ======
def confirm_answer():
    if not st.session_state.show_answer:
        # 第一次按 → 顯示答案
        st.session_state.show_answer = True
    else:
        # 第二次按 → 換下一題
        new_question()

# ====== 首頁：選擇使用者 ======
if st.session_state.user is None:
    st.markdown("<h2 style='font-family: Times New Roman; text-align:center;'>Select User</h2>", unsafe_allow_html=True)
    st.button("Alex", key="alex_btn", on_click=lambda: select_user("Alex"))
    st.button("Eveline", key="eve_btn", on_click=lambda: select_user("Eveline"))

else:
    # ====== 題目頁 ======
    st.markdown(f"<div class='title-box'>IELTS Vocabulary Practice ({st.session_state.user})</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='word'>{st.session_state.question}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='phonetic'>{st.session_state.phonetic}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='example'>{st.session_state.example}</div>", unsafe_allow_html=True)

    if st.session_state.show_answer:
        st.info(f"正確答案：{st.session_state.correct}")

    st.session_state.input_text = st.text_input("請輸入中文意思", value=st.session_state.input_text)
    st.button("確認", on_click=confirm_answer)
