from uuid import uuid4
from qdrant_client import QdrantClient
from qdrant_client.http.models import Batch, VectorParams
import nltk
from json import loads
from openai import OpenAI
from firecrawl import FirecrawlApp
from nltk.tokenize import sent_tokenize

from typing import List, Dict, Tuple

from app.utilities.logger import logger
from config import (FIRECRAWL_API_KEY, EMBEDDING_MODEL_NAME, VECTOR_DIMENSION, VECTOR_DB_PATH, DEFAULT_COLLECTION_NAME,
                    OPENAI_LLM_MODEL, PROMPT_REPHRASE_QUERY, PROMPT_GENERATE_ANSWER, OPENAI_API_KEY)

nltk.download('punkt_tab')
qclient = QdrantClient(path=VECTOR_DB_PATH)
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def process_urls_for_indexing(urls: List, collection_name: str = DEFAULT_COLLECTION_NAME) -> Tuple:
    """
    This function takes care of all the steps required to insert data
    from each URL into the vector database.
    :param urls: list
    :param collection_name: str
    :return: tuple
    """
    indexed_url, failed_url = [], []

    # Iterating over the URLs list to scrape, chunk and store content in vector DB
    for url in urls:
        try:
            # Scrape the url content
            scrapped_data = scrape_content_from_url(url)

            # Convert scraped text into chunks
            chunks = get_chunks(scrapped_data, chunk_sentences=10)

            # Insert data into the vector DB.
            payloads, ids, embeddings = [], [], []

            for chunk in chunks:
                payloads.append({"text": chunk, "url": url})
                ids.append(str(uuid4()))
                embeddings.append(encode_text(chunk))

            # Upsert data to Qdrant collection
            qclient.upsert(
                collection_name=collection_name,
                points=Batch(ids=ids, vectors=embeddings, payloads=payloads)
            )
            indexed_url.append(url)
        except Exception as err:
            logger.error('Error while inserting url into the vector DB:', str(err))
            failed_url.append(url)

    return indexed_url, failed_url


def scrape_content_from_url(url: str) -> str:
    """
    This function scrape the content from a URL using Firecrawl API
    and returns the content in the form of text.
    :param url: list
    :return: str
    """
    try:
        # Calling Firecrawl API to scrape the content from URL.
        app = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

        response = app.scrape_url(url=url, params={
            'formats': ['markdown', 'links'],
        })

        return response['markdown']

    except Exception as err:
        logger.error('Error while scraping the content from the URL:', str(err))
        raise Exception(err)


def get_chunks(text: str, chunk_sentences: int = 10, overlap_chunk_sentences: int = 1) -> List:
    """
    This function creates smaller chunks out of big text content.
    :param text: str
    :param chunk_sentences: int
    :param overlap_chunk_sentences: int
    :return: list
    """
    try:
        # Tokenizing the text into sentences
        sentences = sent_tokenize(text)

        # Remove unnecessary whitespace from sentences
        sentences = [sentence.strip() for sentence in sentences]

        chunks = []
        start_index = 0
        # Create chunks with overlap
        while start_index < len(sentences):
            # Define the end of the chunk
            end_index = start_index + chunk_sentences
            chunk = sentences[start_index:end_index]
            chunks.append(' '.join(chunk))  # Convert chunk into a single string

            # Move the start index forward by the chunk size minus the overlap
            start_index = max(0, start_index + chunk_sentences - overlap_chunk_sentences)

        return chunks
    except Exception as err:
        logger.error('Error while converting text to chunks:', str(err))
        raise Exception(err)


def create_collection(collection_name: str) -> bool:
    """
    This function creates a new collection in Qdrant vector DB.
    :param collection_name: str
    :return: bool
    """
    try:
        status = qclient.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=VECTOR_DIMENSION, distance="Cosine")
        )
        return status
    except Exception as err:
        logger.error('Error while creating a new collection in vector DB:', str(err))
        raise Exception(err)


def fetch_all_records(collection_name: str = DEFAULT_COLLECTION_NAME, limit: int = 10) -> list:
    """
    Retrieve all records from a collection with an optional limit.
    :param collection_name: str
    :param limit: int
    :return: list
    """
    try:
        points = qclient.scroll(collection_name=collection_name, limit=limit)
        return [{"id": point.id, "payload": point.payload} for point in points[0]]

    except Exception as err:
        logger.error('Error while fetching the records from vector DB:', str(err))
        raise Exception(err)


def generate_query_response(previous_chat: str, current_query: str) -> Tuple:
    """
    This function checks for relevant chunks in the db and generates the response.
    :param previous_chat: str
    :param current_query: str
    :return: tuple
    """
    try:
        if previous_chat != '':
            # Given the previous chat and current query, generate the relevant query
            # with the help of LLMs that needs to be searched in the vector DB
            rephrased_query = generate_query_for_searching(previous_chat, current_query)
            print(rephrased_query)
        else:
            rephrased_query = current_query

        # Search the relevant chunks in the vector DB
        query_embedding = encode_text(rephrased_query)
        search_result = qclient.search(
            collection_name=DEFAULT_COLLECTION_NAME,
            query_vector=query_embedding,
            limit=5
        )

        # if search_result[0].score < 0.3:
        #     return "I don't quite get that. I don't have this information.", []

        citation_links = []

        # Prepare Context
        contexts = ""
        for result in search_result:
            contexts += result.payload['text'] + "\n---\n"
            citation_links.append(result.payload['url'])


        llm_response, is_query_relevant = generate_response_from_context(contexts, current_query)
        if loads(is_query_relevant):
            return llm_response, list(set(citation_links))
        else:
            return llm_response, []

    except Exception as err:
        logger.error('Error while generating the response to the current query:', str(err))
        raise Exception(err)


def generate_query_for_searching(previous_chat: str, current_query: str) -> str:
    """
    This function calls a LLM to generate the relevant query based on the context.
    :param previous_chat: str
    :param current_query: str
    :return: str
    """
    try:
        system_prompt = "You are a helpful assistant having expertise in analysing chat history and proving output in JSON format."
        prompt = PROMPT_REPHRASE_QUERY.replace('{previous_chat}', previous_chat).replace('{current_query}', current_query)
        response = openai_client.chat.completions.create(
            model=OPENAI_LLM_MODEL,
            messages=[
                {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ],
            temperature=0,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_object"
            }
        )
        response = loads(response.choices[0].message.content)['response']
        return response
    except Exception as err:
        logger.error('Error while generating the relevant query for searching the db:', str(err))
        raise Exception(err)


def generate_response_from_context(context: str, current_query: str) -> Tuple:
    """
    This function calls a LLM to generate the relevant response based on the context.
    :param context: str
    :param current_query: str
    :return: str
    """
    try:
        system_prompt = "You are a helpful assistant having expertise in answering the question in JSON format based on given context."
        prompt = PROMPT_GENERATE_ANSWER.replace('{documents}', context).replace('{user_query}', current_query)
        response = openai_client.chat.completions.create(
            model=OPENAI_LLM_MODEL,
            messages=[
                {"role": "system", "content": [{"type": "text", "text": system_prompt}]},
                {"role": "user", "content": [{"type": "text", "text": prompt}]}
            ],
            temperature=0.3,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={
                "type": "json_object"
            }
        )
        message = loads(response.choices[0].message.content)['response']
        is_query_relevant = loads(response.choices[0].message.content)['is_query_relevant']
        return message, is_query_relevant
    except Exception as err:
        logger.error('Error while generating the relevant answer for the given query:', str(err))
        raise Exception(err)


def encode_text(text: str) -> List:
    """
    This function uses openai text embeddings to convert a text into the vectors.
    :param text: str
    :return: list
    """
    try:
        response = openai_client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL_NAME
        )

        return response.data[0].embedding
    except Exception as err:
        logger.error('Error while generating the text embeddings:', str(err))
        raise Exception(err)