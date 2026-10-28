import re
from pathlib import Path

import streamlit as st
from google import genai
from google.genai.errors import APIError
from streamlit.errors import StreamlitSecretNotFoundError

MODEL_NAME = "gemini-3.8-flash"
APP_DIR = Path(__file__).resolve().parent

st.set_page_config(page_title="mytaller.info AI assistant")
st.title("mytaller.info AI assistant")
st.caption("Ask about the neighborhood watch or room rentals.")


def load_documents() -> list[str]:
    documents = []
    for filename in ("security.txt", "rental.txt"):
        path = APP_DIR / filename
        if path.exists():
            text = path.read_text(encoding="utf-8")
            documents.extend(
                paragraph.strip()
                for paragraph in text.split("\n\n")
                if paragraph.strip()
            )
    return documents


def find_most_relevant_context(user_query: str, docs: list[str]) -> str:
    query_words = set(re.findall(r"\w+", user_query.lower()))
    if not docs:
        return ""
    return max(
        docs,
        key=lambda doc: len(
            query_words.intersection(re.findall(r"\w+", doc.lower()))
        ),
    )


documents = load_documents()
if not documents:
    st.error("The knowledge base is empty. Add content to security.txt or rental.txt.")
    st.stop()

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except (KeyError, StreamlitSecretNotFoundError):
    st.error(
        "Gemini API key is not configured. Add GEMINI_API_KEY to "
        "Streamlit Community Cloud's app Secrets."
    )
    st.stop()

client = genai.Client(api_key=api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Type your question"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    context = find_most_relevant_context(question, documents)
    instructions = (
        "You are a helpful assistant for mytaller.info. Answer using only the "
        "provided context. If the context does not contain the answer, say you "
        "don't know.\n\n"
        f"Context:\n{context}"
    )

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = client.interactions.create(
                    model=MODEL_NAME,
                    input=f"{instructions}\n\nUser question: {question}",
                )
                answer = response.output_text
            except APIError as error:
                st.error(f"Could not get a response from Gemini: {error}")
                st.stop()
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
