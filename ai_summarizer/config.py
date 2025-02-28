import os
from pathlib import Path

class Config:
    ALLOWED_FILE_EXTENSIONS = set(['.pdf', '.md', '.txt'])

    class Model:
        NAME = "deepseek-r1:14b"
        TEMPERATURE = 0.0

    class Preprocessing:
        CHUNK_SIZE = 2048
        CHUNK_OVERLAP = 128
        EMBEDDING_MODEL = "deepseek-r1:14b"
        CONTEXTUALIZE_CHUNKS = True

    class Chatbot:
        N_CONTEXT_RESULTS = 200
    
    class Path:
        APP_HOME = Path(os.getenv("APP_HOME", Path(__file__).parent.parent))
    
    class Prompt:
        SYSTEM_PROMPT = "No debes inventar ni añadir información, solo proporcionar las respuestas respecto a la información que está presente en el documento:\n\n{document}\n\nPregunta: {question}\n\nContexto de la conversación:{context}\n\nRespuesta:"
