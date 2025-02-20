import os
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate

class Config:
    ALLOWED_FILE_EXTENSIONS = set(['.pdf', '.md', '.txt'])

    class Model:
        NAME = "deepseek-r1"
        TEMPERATURE = 0.6

    class Preprocessing:
        CHUNK_SIZE = 2048
        CHUNK_OVERLAP = 128
        EMBEDDING_MODEL = "deepseek-r1"
        CONTEXTUALIZE_CHUNKS = True

    class Chatbot:
        N_CONTEXT_RESULTS = 200
    
    class Path:
        APP_HOME = Path(os.getenv("APP_HOME", Path(__file__).parent.parent))
    
    class Prompt:
        TEMPLATE = ChatPromptTemplate.from_messages([("system", "{system_prompt}"),("user", "Utiliza el siguiente documento como contexto para responder la pregunta del usuario:\n\n{document}\n\nPregunta: {question}\n\nContexto de la conversación:{context}\n\nRespuesta:")])
        SYSTEM_PROMPT = "Eres una IA que ayuda a los usuarios a responder preguntas sobre documentos. Utiliza el siguiente documento como contexto para responder la pregunta del usuario:\n\n{document}\n\nPregunta: {question}\n\nContexto de la conversación:{context}\n\nRespuesta:"