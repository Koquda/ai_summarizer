import json
import os
import re
import logging
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from ai_summarizer.config import Config

# Configurar logging
logger = logging.getLogger(__name__)

def process_llm_response(response):
    """Process the LLM response and extract think content and response text."""
    try:
        think_match = re.search(r'<think>(.*?)</think>', response.content, re.DOTALL)
        think_content = think_match.group(1).strip() if think_match else ""
        response_text = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip()
        
        logger.debug(f"Processed LLM response - Think content length: {len(think_content)}")
        return think_content, response_text
        
    except AttributeError as e:
        logger.error(f"Invalid response format: {e}")
        raise ValueError("Invalid response format from LLM")
    except Exception as e:
        logger.error(f"Error processing LLM response: {e}")
        raise

def generate_response(chain, query, vector_store):
    """Generate response using the LLM chain."""
    try:
        # Verify query is not None or empty
        if not query:
            logger.error("Empty query received")
            raise ValueError("Query cannot be empty")

        # Load configuration for the system prompt
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, "config.json")
        
        try:
            with open(config_path) as f:
                config = json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found at: {config_path}")
            raise
        except json.JSONDecodeError:
            logger.error("Invalid JSON in config file")
            raise
            
        if "system_prompt" not in config:
            logger.error("Missing system_prompt in config")
            raise ValueError("system_prompt not found in config.json")

        # Retrieve relevant document chunks using similarity search
        logger.info(f"Performing similarity search for query: {query[:50]}...")
        search_results = vector_store.similarity_search(query, k=Config.Chatbot.N_CONTEXT_RESULTS)
        document_content = "\n".join([doc.page_content for doc in search_results])

        if not document_content:
            logger.warning("No relevant documents found in vector store")
            raise ValueError("No document content retrieved from vector store")

        # Get conversation history from session state 
        conversation_context = ""
        if "messages" in st.session_state:
            logger.debug(f"Building context from {len(st.session_state.messages)} messages")
            for message in st.session_state.messages:
                if message["role"] == "user":
                    conversation_context += f"Usuario: {message['content']}\n"
                else:
                    conversation_context += f"Asistente: {message['response']}\n"

        # Call chain.invoke() with properly formatted input
        logger.info("Invoking LLM chain")
        response = chain.invoke({
            "document": document_content,
            "question": query,
            "context": conversation_context
        })
        
        logger.info("Chain invoked successfully")

        think_content, response_text = process_llm_response(response)
        
        st.session_state.messages.append({
            "role": "assistant", 
            "response": response_text,
            "think": think_content
        })
        
        logger.info("Response processed and saved to session state")
        return response_text

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_response: {str(e)}")
        raise