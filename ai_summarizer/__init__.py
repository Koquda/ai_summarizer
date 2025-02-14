import streamlit as st
import os
import json
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader

# Initialize the LLM
llm = ChatOllama(
    model="deepseek-r1",
    temperature=0.5,
)

st.title("Document Chatbot")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# File uploader widget for txt, md, or pdf files
uploaded_file = st.file_uploader("Upload a file", type=["txt", "md", "pdf"])

if uploaded_file is not None:
    file_ext = os.path.splitext(uploaded_file.name)[1].lower()
    
    # Process file based on its extension
    if file_ext == '.txt':
        content = uploaded_file.read().decode("utf-8")
        documents = [Document(page_content=content)]
    elif file_ext == '.md':
        content = uploaded_file.read().decode("utf-8")
        documents = [Document(page_content=content)]
    elif file_ext == '.pdf':
        temp_path = f"temp{file_ext}"
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        loader = PyPDFLoader(temp_path)
        documents = loader.load()
        os.remove(temp_path)
    else:
        st.error("Unsupported file type")

    # Combine content from all loaded documents
    combined_content = "\n\n".join([doc.page_content for doc in documents])

    # Load configuration for the system prompt
    with open("config.json") as f:
        config = json.load(f)

    # Define the chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", config["system_prompt"]),
        ("user", "Utiliza el siguiente documento como contexto para responder la pregunta del usuario:\n\n{document}\n\nPregunta: {user_query}\nRespuesta:")
    ])

    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input field at the bottom, send on Enter
    def send_message():
        user_query = st.session_state.user_input.strip()
        if user_query:
            # Store user message
            st.session_state.messages.append({"role": "user", "content": user_query})

            # Generate response
            chain = prompt.partial(document=combined_content, user_query=user_query) | llm
            response = chain.invoke({}).content

            # Store assistant's response
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Clear input field
            st.session_state.user_input = ""

    st.text_input("Type your message...", key="user_input", on_change=send_message)

