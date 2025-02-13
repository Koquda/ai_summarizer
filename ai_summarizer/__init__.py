import json
import os
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_community.document_loaders import TextLoader, PyPDFLoader, UnstructuredMarkdownLoader 

print("Current working directory:", os.getcwd())

# Initialize the LLM
llm = ChatOllama(
    model="deepseek-r1",
    temperature=0.5,
)

# Configure file loading
file_path = 'recipe.md'  # Change this to your input file
file_ext = os.path.splitext(file_path)[1].lower()

print(f"Loading {file_ext} document...")

# Select the appropriate loader based on file extension
if file_ext == '.txt':
    loader = TextLoader(file_path, encoding='utf-8')
elif file_ext == '.md':
    loader = UnstructuredMarkdownLoader(file_path)
elif file_ext == '.pdf':
    loader = PyPDFLoader(file_path)
else:
    raise ValueError(f"Unsupported file type: {file_ext}")

# Load and combine content from the document
documents = loader.load()
combined_content = "\n\n".join([doc.page_content for doc in documents])

# Load configuration from config.json
with open("config.json") as f:
    config = json.load(f)

# Define a chat prompt template that includes the document context.
# The prompt instructs the model to answer the user's question based on the document.
prompt = ChatPromptTemplate.from_messages([
    ("system", config["system_prompt"]),
    ("user", "Utiliza el siguiente documento como contexto para responder la pregunta del usuario:\n\n{document}\n\nPregunta: {user_query}\nRespuesta:")
])

print("Chatbot is ready! Type 'exit' to quit.")

# Chat loop: repeatedly get user input and generate a response
while True:
    user_query = input("You: ")
    if user_query.lower() in ["exit", "quit"]:
        print("Exiting chatbot.")
        break

    # Fill in the prompt with the document and the user’s query, then call the LLM
    chain = prompt.partial(document=combined_content, user_query=user_query) | llm
    response = chain.invoke({})
    print("Bot:", response.content)
