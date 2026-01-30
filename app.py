import streamlit as st
from openai import OpenAI

# -----------------------------
# 基本設定
# -----------------------------
APP_TITLE = "Samurai & Shinsengumi AI Guide"

MAX_INPUT_CHARS = 200
MAX_OUTPUT_TOKENS = 180  # 出力を短くしてAPIコスト節約

SYSTEM_PROMPT = (
    "You are a friendly and knowledgeable English guide explaining the Shinsengumi "
    "to international visitors. Keep answers clear, simple, and under 500 characters."
)

# 表示する質問文をそのままボタンに使う
QUESTIONS = [
    "Who were the Shinsengumi?",
    "What was the Shinsengumi’s role in Japanese history?",
    "When did the Shinsengumi exist?",
    "Where were the Shinsengumi mainly active?",
    "Why were the Shinsengumi formed?",
    "How did the Shinsengumi fight in battle?",
    "What was the Shinsengumi’s code of conduct, and why was it so important?"
]

# -----------------------------
# セッション初期化
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "menu"

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "last_question" not in st.session_state:
    st.session_state.last_question = ""

if "last_answer" not in st.session_state:
    st.session_state.last_answer = ""

# -----------------------------
# 共通関数
# -----------------------------
def call_openai(api_key, user_question):
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_question},
        ],
        max_tokens=MAX_OUTPUT_TOKENS,
        temperature=0.5,
    )

    return response.choices[0].message.content.strip()


def go_to_answer(question, api_key):
    try:
        answer = call_openai(api_key, question)
        st.session_state.last_question = question
        st.session_state.last_answer = answer
        st.session_state.page = "answer"
        st.rerun()
    except Exception as e:
        st.error("Error calling OpenAI API. Please check your API key.")
        st.write(str(e))


# -----------------------------
# UI
# -----------------------------
st.set_page_config(page_title=APP_TITLE, layout="centered")
st.title(APP_TITLE)

st.write("Learn about the Shinsengumi in English using your own OpenAI API key.")
st.warning("Your API key is used only in this session. Usage will be billed to your OpenAI account.")

# -----------------------------
# APIキー入力
# -----------------------------
api_key_input = st.text_input(
    "Enter your OpenAI API Key",
    type="password",
    value=st.session_state.api_key,
    help="This key is required to use the chatbot. Your OpenAI account will be charged."
)

st.session_state.api_key = api_key_input.strip()

if not st.session_state.api_key or len(st.session_state.api_key) < 20:
    st.info("Please enter a valid OpenAI API key to continue.")
    st.stop()

# -----------------------------
# メニュー画面
# -----------------------------
if st.session_state.page == "menu":
    st.subheader("Choose a question")

    cols = st.columns(2)

    for i, question in enumerate(QUESTIONS):
        with cols[i % 2]:
            if st.button(question):
                go_to_answer(question, st.session_state.api_key)

    st.divider()

    # 自由質問
    st.subheader("Ask your own question (English)")
    user_input = st.text_area(
        f"Max {MAX_INPUT_CHARS} characters",
        max_chars=MAX_INPUT_CHARS,
        height=100
    )

    if st.button("Ask"):
        if not user_input.strip():
            st.warning("Please enter a question.")
        else:
            go_to_answer(user_input.strip(), st.session_state.api_key)

# -----------------------------
# 回答画面
# -----------------------------
elif st.session_state.page == "answer":
    st.subheader("Your Question")
    st.write(st.session_state.last_question)

    st.subheader("AI Answer")
    st.write(st.session_state.last_answer)

    st.divider()

    if st.button("Back to Menu"):
        st.session_state.page = "menu"
        st.rerun()
