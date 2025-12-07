import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_community.document_loaders import PyMuPDFLoader

load_dotenv(".env")
llm = ChatGoogleGenerativeAI(
    model = "gemini-2.5-flash",
    temperature = 2,
    # max_output_tokens = 1024,
    timeout=None,
    max_retries=2,
)
SYSTEM_PROMPT = """
You are a helpful document assistant. Answer all questions based on the provided PDF document.\n
PDF Content:\n{docs}
"""
st.title("Custom Chatbot")
file_uploader = st.file_uploader("Choose a PDF file", type=["pdf"], accept_multiple_files=False)
if file_uploader is not None:
    file_path = f"docs/{file_uploader.name}"
    with open(file_path, "wb") as f:
        f.write(file_uploader.getbuffer())
    st.session_state["file_path"] = file_path
    st.success(f"File saved to: {file_path}")
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    docs = "".join([doc.page_content for doc in documents])
    # st.write(docs)
    st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT.format(docs=docs)})
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(docs=docs) if 'docs' in locals() else "No document loaded."}
    ]
else:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        elif message["role"] == "assistant":
            st.chat_message("assistant").write(message["content"])
user_message =  st.chat_input("Enter your message:")
if user_message:
    st.chat_message("user").write(user_message)

    st.session_state.messages.append({"role": "user", "content": user_message})
    with st.chat_message("assistant"):
        stream = llm.stream(st.session_state.messages)
        response = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response})