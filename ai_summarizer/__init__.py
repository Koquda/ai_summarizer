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
        # PyPDFLoader expects a path, so you may need to save the file temporarily
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
    
    # Define the chat prompt template that includes the document context.
    prompt = ChatPromptTemplate.from_messages([
        ("system", config["system_prompt"]),
        ("user", "Utiliza el siguiente documento como contexto para responder la pregunta del usuario:\n\n{document}\n\nPregunta: {user_query}\nRespuesta:")
    ])
    
    # Text input for the user to ask a question
    user_query = st.text_input("Enter your question:")
    
    if st.button("Send") and user_query:
        # Fill in the prompt with both the document and the user query
        chain = prompt.partial(document=combined_content, user_query=user_query) | llm
        response = chain.invoke({})
        st.write(response.content)
