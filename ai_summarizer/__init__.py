import re
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
print("Model loaded")

st.title("Document Chatbot")

# Initialize session state for messages if not already done
if "messages" not in st.session_state:
    st.session_state.messages = []

# File uploader widget for txt, md, or pdf files
uploaded_file = st.file_uploader("Upload a file", type=["txt", "md", "pdf"])

# Process the uploaded file only if it is new
if uploaded_file is not None:
    # Check if we have already processed this file
    if "uploaded_file_name" not in st.session_state or st.session_state.uploaded_file_name != uploaded_file.name:
        st.session_state.uploaded_file_name = uploaded_file.name
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        
        # Process file based on its extension
        if file_ext == '.txt':
            content = uploaded_file.read().decode("utf-8")
            documents = [Document(page_content=content)]
        elif file_ext == '.md':
            content = uploaded_file.read().decode("utf-8")
            documents = [Document(page_content=content)]
        elif file_ext == '.pdf':
            # Save temporary file for PDF processing
            temp_path = f"temp{file_ext}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            loader = PyPDFLoader(temp_path)
            documents = loader.load()
            os.remove(temp_path)
        else:
            st.error("Unsupported file type")
        
        # Combine content from all loaded documents and store in session state
        combined_content = "\n\n".join([doc.page_content for doc in documents])
        st.session_state.combined_content = combined_content
else:
    # If no file is uploaded, check if we have a stored document
    if "combined_content" not in st.session_state:
        st.warning("Please upload a file to get started.")
        st.stop()

# Load configuration for the system prompt
with open("config.json") as f:
    config = json.load(f)

# Define the chat prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", config["system_prompt"]),
    ("user", "Utiliza el siguiente documento como contexto para responder la pregunta del usuario:\n\n{document}\n\nPregunta: {user_query}\nRespuesta:")
])

# Get user input and handle Enter key
if user_input := st.chat_input("Enter your question:"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "response": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    
    with st.spinner("Pensando..."):
        # Generate response using stored combined_content
        chain = prompt_template.partial(
            document=st.session_state.combined_content, 
            user_query=user_input
        ) | llm

        print("Invoking chain")

        response = chain.invoke({})

        print("Chain invoked")

        think_match = re.search(r'<think>(.*?)</think>', response.content, re.DOTALL)
        think_content = think_match.group(1).strip() if think_match else ""
        
        # Remove the <think> tag and its content from the text
        response_text = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip()
        
        # Add assistant response to chat history
        st.session_state.messages.append({
            "role": "assistant", 
            "response": response_text, 
            "think": think_content
        })

# Display the entire chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            with st.expander("Razonamiento del modelo"):
                st.markdown(message["think"])
        st.markdown(message["response"])
        if message["role"] == "assistant":
            with st.expander("Documento utilizado"):
                st.markdown(st.session_state.combined_content)
