import os
import nest_asyncio
import pandas as pd
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ragas.llms import LangchainLLMWrapper
from langchain_openai import ChatOpenAI
from ragas.testset import TestsetGenerator
from ragas.dataset_schema import EvaluationDataset
#from ragas.testset.synthesizers import SpecificQuerySynthesizer, ComparativeAbstractQuerySynthesizer #Não existem mais
from ragas.testset.synthesizers.single_hop.specific import SingleHopSpecificQuerySynthesizer
from ragas.testset.synthesizers.multi_hop.specific import MultiHopSpecificQuerySynthesizer

#from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import OpenAIEmbeddings

# Apply nest_asyncio to avoid event loop issues
nest_asyncio.apply()


# Load OpenAI API key from environment variables or .env file
load_dotenv()  # Ensure you have a .env file with OPENAI_API_KEY
openai_api_key = os.getenv("OPENAI_API_KEY")

#Tive que incluir
generator_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings())

# Verify if the key was loaded correctly
if openai_api_key is None:
    raise ValueError("OpenAI API Key not found. Please ensure you have a .env file with 'OPENAI_API_KEY'.")


# Check if the Weave repository already exists; if not, download it using sparse checkout
repo_dir = "weave_docs"
if not os.path.exists(repo_dir):
    os.system(f"git init {repo_dir}")
    os.chdir(repo_dir)
    os.system("git remote add origin https://github.com/wandb/weave.git")
    os.system("git sparse-checkout init --cone")
    os.system("git sparse-checkout set docs/docs/guides/tracking")
    os.system("git pull origin master")
    os.chdir("..")
else:
    print(f"{repo_dir} already exists, skipping download.")


path = os.path.join(repo_dir, "docs/docs/guides/tracking")
loader = DirectoryLoader(path, glob="**/*.md")
docs = loader.load()


# Split the documents into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)


# Wrap the LLM with LangchainLLMWrapper using OpenAI GPT-4 model
evaluator_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4o"))


# Generate the test set with the loaded documents (generating 30 examples)
generator = TestsetGenerator(llm=evaluator_llm, embedding_model=generator_embeddings)


# Assuming the function signature doesn't accept `docs`, pass splits as positional argument
# dataset = generator.generate_with_langchain_docs(splits, testset_size=30)
query_distribution = [
    (MultiHopSpecificQuerySynthesizer(llm=evaluator_llm), 0.5),
    (SingleHopSpecificQuerySynthesizer(llm=evaluator_llm), 0.5),
]


# Call the generate_with_langchain_docs with the custom query_distribution
dataset = generator.generate_with_langchain_docs(
    splits, 
    testset_size=30, 
    query_distribution=query_distribution
)


# Convert the generated dataset to a Pandas DataFrame
df = dataset.to_pandas()
print(df)


# Optionally, save the generated testset to a CSV file for further inspection
output_csv_path = "generated_testset.csv"
df.to_csv(output_csv_path, index=False)
print(f"Generated testset saved to {output_csv_path}")
