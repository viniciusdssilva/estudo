import os
import nest_asyncio
import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain import hub
import time 
# Apply nest_asyncio to avoid event loop issues
nest_asyncio.apply()


# Load API keys
load_dotenv()


anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
if anthropic_api_key is None:
    raise ValueError("Anthropic API Key not found.")


#cohere_api_key = os.getenv("COHERE_API_KEY")
#if cohere_api_key is None:
    #raise ValueError("Cohere API Key not found.")


# Models to iterate through
gen_models = ["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
embed_models = ["openai"]




# Set up the path to your dataset and vector stores
repo_dir = "weave_docs"
if not os.path.exists(repo_dir):
    os.system(f"git init {repo_dir}")
    os.chdir(repo_dir)
    os.system("git remote add origin https://github.com/wandb/weave.git")
    os.system("git sparse-checkout init --cone")
    os.system("git sparse-checkout set docs/docs/guides/tracking")
    os.system("git pull origin master")
    os.chdir("..")


path = os.path.join(repo_dir, "docs/docs/guides/tracking")
loader = DirectoryLoader(path, glob="**/*.md")
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)


# Function to select the appropriate embedding model
def get_embeddings(embed_model):
    if embed_model == "openai":
        return OpenAIEmbeddings()
    elif embed_model == "cohere":
        return CohereEmbeddings(model="embed-english-v3.0")


# Iterate over generation and embedding models
for gen_model, embed_model in zip(gen_models, embed_models):
    print(f"Processing {gen_model} with {embed_model} embeddings...")


    vectorstore_dir = f"vectorstore_{gen_model}_{embed_model}"
    if os.path.exists(vectorstore_dir):
        print(f"Loading vector store from cache: {vectorstore_dir}")
        vectorstore = Chroma(persist_directory=vectorstore_dir, embedding_function=get_embeddings(embed_model))
    else:
        print(f"Creating vector store for {gen_model} and {embed_model}...")
        vectorstore = Chroma.from_documents(documents=splits, embedding=get_embeddings(embed_model), persist_directory=vectorstore_dir)


    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")


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


    # Select the appropriate LLM
    if "claude" in gen_model:
        model = ChatAnthropic(model=gen_model)
    else:
        model = ChatOpenAI(model=gen_model)


    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RunnableLambda(capture_retrieved_contexts)
        | prompt
        | model
        | StrOutputParser()
    )


    # Load and evaluate dataset
    file_path = "./generated_testset.csv"
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
    output_csv_path = f"./results_{gen_model}_{embed_model}.csv"
    data['response'] = responses
    data['retrieved_contexts'] = retrieved_contexts_list
    data.to_csv(output_csv_path, index=False)
    print(f"Saved results to {output_csv_path}")
