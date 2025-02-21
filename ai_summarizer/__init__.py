import re
import streamlit as st
import os
import json
import logging
from ai_summarizer.retrieval_chain import create_chain, create_vector_store
from ai_summarizer.response_generator import generate_response
from ai_summarizer.custom_formatter import CustomFormatter

# Configurar logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Avoid adding multiple handlers
if not logger.handlers:
    # Crear y configurar el handler con el CustomFormatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    # También podemos añadir un FileHandler para guardar los logs en un archivo
    file_handler = logging.FileHandler('chatbot.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)

def initialize_session_state():
    """Inicializa las variables del estado de la sesión"""
    try:
        if "vector_store" not in st.session_state:
            st.session_state.vector_store = create_vector_store(None)
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "is_generating" not in st.session_state:
            st.session_state.is_generating = False
    except Exception as e:
        logger.error(f"Error initializing session state: {str(e)}")
        st.error("Error initializing application. Please try refreshing the page.")
        st.stop()

def ask_question(query: str) -> None:
    """
    Procesa una pregunta utilizando el vector store y genera una respuesta
    
    Args:
        query: La pregunta del usuario
    """
    try:
        vector_store = st.session_state.vector_store
        logger.info(f"Processing question: {query}")
        
        chain = create_chain()
        logger.info("Chain created successfully")
        
        generate_response(chain, query, vector_store)
        logger.info("Response generated successfully")
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        st.error("Lo siento, ha ocurrido un error al procesar tu pregunta. Por favor, inténtalo de nuevo.")

def main():
    try:
        st.title("Document Chatbot")
        initialize_session_state()

        chat_container = st.container()
        summary_container = st.container()

        # File uploader widget
        uploaded_file = st.file_uploader("Upload a file", type=["txt", "md", "pdf"])

        if uploaded_file is not None:
            logger.info(f"Processing file: {uploaded_file.name}")
            try:
                st.session_state.vector_store = create_vector_store(uploaded_file)
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
                st.error("Error processing the uploaded file. Please check the file format and try again.")
                st.stop()
        else:
            if "combined_content" not in st.session_state:
                st.warning("Please upload a file to get started.")
                st.stop()

        with chat_container:
            if user_input := st.chat_input("Enter your question:", disabled=st.session_state.is_generating):
                logger.info(f"New user input received: {user_input}")
                st.session_state.is_generating = True
                st.session_state.current_input = user_input
                with st.spinner("Pensando..."):
                    try:
                        st.session_state.messages.append({
                            "role": "user",
                            "content": user_input
                        })
                        ask_question(st.session_state.current_input)
                    except Exception as e:
                        logger.error(f"Error in chat interaction: {str(e)}")
                    finally:
                        st.session_state.is_generating = False
                        if "current_input" in st.session_state:
                            del st.session_state.current_input
                        st.rerun()

        with summary_container:
            if st.button("Summarize document", disabled=st.session_state.is_generating):
                logger.info("Summary requested")
                st.session_state.is_generating = True
                st.session_state.summarize_requested = True
                st.session_state.messages = []
                with st.spinner("Summarizing..."):
                    try:
                        question = "Realiza un resumen del documento"
                        st.session_state.messages.append({
                            "role": "user",
                            "content": question
                        })
                        ask_question(question)
                    except Exception as e:
                        logger.error(f"Error generating summary: {str(e)}")
                        st.error("Error generating document summary")
                    finally:
                        st.session_state.is_generating = False
                        st.session_state.summarize_requested = False
                        st.rerun()

        # Display chat history
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    with st.expander("Razonamiento del modelo"):
                        st.markdown(message["think"])
                    st.markdown(message["response"])
                
                if message["role"] == "user":
                    st.markdown(message["content"])
                logger.info(f"Message displayed: {message}")


    except Exception as e:
        logger.error(f"Unexpected error in main application: {str(e)}")
        st.error("An unexpected error occurred. Please refresh the page and try again.")

if __name__ == "__main__":
    main()
