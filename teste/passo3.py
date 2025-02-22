import os
import nest_asyncio
import pandas as pd
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
import time 
#
from langchain_milvus import Milvus
from prompt2 import prompt_template
#import formatter as frmtr


# Apply nest_asyncio to avoid event loop issues
nest_asyncio.apply()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

EMBEDDINGS_MODEL_NAME = "text-embedding-3-large"
DB_URI = "http://localhost:19530"
COLLECTION_NAME = "ASRC_42_P_3L_RS_2000_400"

embeddings_model = OpenAIEmbeddings(model=EMBEDDINGS_MODEL_NAME)

#Meu llm no reader
model = ChatOpenAI(model="gpt-4o-mini")

vector_db: Milvus = Milvus(
    embedding_function=embeddings_model,
    collection_name=COLLECTION_NAME,
    connection_args={"uri": DB_URI,},
)

retriever = vector_db.as_retriever()

#Eu já tenho um formatter, mas deixa assim por enquanto
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Capture retrieved contexts
retrieved_contexts_list = []

def capture_retrieved_contexts(state):
    """Capture the retrieved contexts and store them for later evaluation."""
    retrieved_docs = state['context']  # Extract the retrieved documents from state
    
    # If the retrieved_docs are strings, we can directly append them
    if isinstance(retrieved_docs, list):
        retrieved_contexts = [doc if isinstance(doc, str) else getattr(doc, 'page_content', str(doc)) for doc in retrieved_docs]
    else:
        # If it's a single string or object
        retrieved_contexts = [retrieved_docs if isinstance(retrieved_docs, str) else getattr(retrieved_docs, 'page_content', str(retrieved_docs))]
    
    retrieved_contexts_list.append(retrieved_contexts)  # Append to the global list
    return state  # Pass the state onward


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | RunnableLambda(capture_retrieved_contexts)
    | prompt_template
    | model
    | StrOutputParser()
)


# Load and evaluate dataset - Aqui eu pego do meu json
file_path = "./2020_MagazineLuiza_pt-BR.csv"
data = pd.read_csv(file_path)

responses = []
retrieved_contexts_list = []

for idx, row in data.iterrows():
    user_input = row['user_input']
    # Add a delay to prevent rate-limiting (e.g., 2 seconds)
    time.sleep(2)  # Adjust the duration based on your API rate limits
    # Generate a response using the RAG chain
    response = rag_chain.invoke(user_input)
    responses.append(response)


# Save results
data['response'] = responses
data['retrieved_contexts'] = retrieved_contexts_list
data.to_json("results.json", index=False)
