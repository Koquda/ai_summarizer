import json
import os
import logging
import streamlit as st
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.vectorstores import InMemoryVectorStore
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ai_summarizer.config import Config
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Configurar logging
logger = logging.getLogger(__name__)

def create_vector_store(doc):
    """Create vector store from document."""
    try:
        embedding = OllamaEmbeddings(model=Config.Preprocessing.EMBEDDING_MODEL)
        logger.info("Created embedding model")

        if doc is None:
            logger.debug("No document provided, creating empty vector store")
            vector_store = InMemoryVectorStore(embedding)
            return vector_store

        logger.info(f"Processing uploaded file: {doc.name if doc else 'None'}")
        documents = process_uploaded_file(doc)
        
        if not documents:
            logger.warning("No documents were processed")
            return InMemoryVectorStore(embedding)

        vector_store = InMemoryVectorStore.from_documents(documents, embedding=embedding)
        logger.info(f"Vector store created successfully with {len(documents)} documents")
        return vector_store

    except Exception as e:
        logger.error(f"Error creating vector store: {str(e)}")
        raise

def create_param_chain(model):
    """Create parameter chain with the given model."""
    try:
        logger.info("Creating parameter chain")
        prompt = ChatPromptTemplate.from_template(Config.Prompt.SYSTEM_PROMPT)
        chain = prompt | model
        logger.debug("Parameter chain created successfully")
        return chain

    except Exception as e:
        logger.error(f"Error in create_param_chain: {str(e)}")
        raise

def create_chain():
    """Create main chain for processing queries."""
    try:
        logger.info("Creating chat model")
        model = ChatOllama(
            model=Config.Model.NAME,
            temperature=Config.Model.TEMPERATURE,
        )
        logger.debug("Chat model created successfully")

        chain = create_param_chain(model)
        logger.info("Main chain created successfully")
        return chain

    except Exception as e:
        logger.error(f"Error creating chain: {str(e)}")
        raise

def process_uploaded_file(uploaded_file):
    """Process uploaded file and return list of Documents."""
    try:
        if uploaded_file is None:
            logger.debug("No file uploaded")
            return []

        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        logger.info(f"Processing file with extension: {file_ext}")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.Preprocessing.CHUNK_SIZE,
            chunk_overlap=Config.Preprocessing.CHUNK_OVERLAP,
            length_function=len,
            add_start_index=True
        )
        
        if file_ext in ['.txt', '.md']:
            content = uploaded_file.read().decode("utf-8")
            texts = text_splitter.split_text(content)
            documents = [Document(page_content=t) for t in texts]
            logger.info(f"Processed text file into {len(documents)} chunks")
            return documents
        
        elif file_ext == '.pdf':
            temp_path = f"temp{file_ext}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            try:
                loader = PyPDFLoader(temp_path)
                documents = loader.load()
                split_docs = text_splitter.split_documents(documents)
                logger.info(f"Processed PDF file into {len(split_docs)} chunks")
                return split_docs
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    logger.debug("Temporary PDF file removed")
        else:
            logger.warning(f"Unsupported file type: {file_ext}")
            st.error("Unsupported file type")
            return []

    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise