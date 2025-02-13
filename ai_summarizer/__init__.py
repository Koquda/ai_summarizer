import json
import os
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama  # Switch to ChatOllama
from langchain_community.document_loaders import TextLoader

print("Current working directory:", os.getcwd())

# Use ChatOllama instead of Ollama for chat models
llm = ChatOllama(
    model="deepseek-r1",
    temperature=0.5,
)

print("Loading document...")
loader = TextLoader('recipe.txt', encoding='utf-8')
documents = loader.load()
combined_content = "\n\n".join([doc.page_content for doc in documents])

with open("config.json") as f:
    config = json.load(f)

    # Create a prompt with explicit roles
    prompt = ChatPromptTemplate.from_messages([
        ("system", config["system_prompt"]),  # General instruction
        ("user", "Summarize this document:\n\n{document}\n\nSummary:")  # Doc + instruction
    ])

    # Build chain with the document injected
    chain = prompt.partial(document=combined_content) | llm

    # Invoke the chain
    response = chain.invoke({})
    print(response.content)