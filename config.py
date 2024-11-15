"""Main configuration file"""

# ######################## #
# #### Configurations #### #
# ######################## #

from dotenv import load_dotenv
from os import getenv, path

from pydantic import Secret

# Loading the env file
load_dotenv('rag.env')

LOG_LEVEL = 'INFO'
PORT = 5000
HOST = '0.0.0.0'

FIRECRAWL_API_KEY = getenv('FIRECRAWL_API_KEY')
OPENAI_API_KEY = getenv('OPENAI_API_KEY')
SECRET_KEY = getenv('SECRET_KEY')

EMBEDDING_MODEL_NAME = "text-embedding-3-small"
OPENAI_LLM_MODEL = "gpt-4o-mini"
VECTOR_DIMENSION = 1536
VECTOR_DB_PATH = "chatbot-rag-db"
DEFAULT_COLLECTION_NAME = "chatbot-rag-db-collection-v1"
PROMPT_GENERATE_ANSWER = """you are an AI agent that can answer user questions based on the knowledge you have from the weblinks.
If the user query is not related to the documents and is about some other topics then just say "I don't quite get that. I don't have this information."
But if the user query is very basic like greetings and salutations, then reply appropriately.

The user asked: {user_query}. Based on the retrieved documents below, please provide a relevant answer to their question which is not too long.
Also, give a flag in the output to indicate if the answer has been given based on the documents.
Documents:
{documents}

Give the output in following JSON format:
{
"response": "",
"is_query_relevant": "true/false"
}"""
PROMPT_REPHRASE_QUERY = """You are an AI agent that can answer user questions based on the knowledge you have from the weblinks.
But before generating the answer, you have to decide if the user query is related to previous chat or a general query for a chatbot like greetings and salutations, etc.
If the query is not relevant to the given chat history then give the same query in the output.
And rephrase the current query based on previous chat history if required, so that the current query can be used to SEARCH THE VECTOR DB for relevant chunks.
Given the previous chat history between a user and a chatbot for a RAG use case.

previous chat:
{previous_chat}

current query:
{current_query}

Give the output in following JSON format:
{
"response": ""
}"""
