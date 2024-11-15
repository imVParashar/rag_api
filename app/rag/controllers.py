from flask import Blueprint, request, jsonify
from app.utilities.logger import logger
from app.utilities import responseHandler
from app.utilities.verify_auth_token import token_required
from app.auth.constants import AuthSuccessMessages
from app.rag.services import process_urls_for_indexing, create_collection, fetch_all_records, generate_query_response
from typing import Dict
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY
import jwt

# Defining the blueprint 'rag'
mod_rag = Blueprint("rag", __name__, url_prefix='/rag')


@mod_rag.route("/api/v1/health", methods=['GET'])
@token_required
def health() -> Dict:
    """
    This method is used for health
    check for auth blueprint.
    @return: JSON
    """
    logger.info(AuthSuccessMessages.HEALTH_CHECK_DONE)
    return responseHandler.success_response(
        AuthSuccessMessages.HEALTH_CHECK_DONE,
        200
    )


@mod_rag.route("/api/v1/index", methods=['POST'])
@token_required
def index_urls() -> Dict:
    """
    This method is used for calling relevant functions for
    indexing the URL contents in vector db.
    @return: JSON
    """
    try:
        request_data = request.json
        urls = request_data['url']

        # For each URL scrape the data and process for indexing in vector DB
        indexed_urls, failed_urls = process_urls_for_indexing(urls)
        status = "success" if len(failed_urls) == 0 else "failure"
        response = {
            "status": status,
            "indexed_url": indexed_urls,
            "failed_url": failed_urls
        }
        return response
    except Exception as err:
        logger.error('Error while indexing the URL content:', str(err))
        return responseHandler.failure_response(
            str(err),
            500
        )


@mod_rag.route("/api/v1/create_collection", methods=['POST'])
@token_required
def create_collection_endpoint():
    try:
        request_data = request.json
        collection_name = request_data['collection_name']
        status = create_collection(collection_name)
        if status:
            return {"status": f"Collection '{collection_name}' created successfully."}
        else:
            return {"error": "Unable to create the collection."}
    except Exception as err:
        logger.error('Error while creating the collection:', str(err))
        return responseHandler.failure_response(
            str(err),
            500
        )

@mod_rag.route("api/v1/fetch_records", methods=['POST'])
@token_required
def fetch_all_records_endpoint():
    try:
        request_data = request.json
        collection_name = request_data['collection_name']
        limit = request_data['limit']
        records = fetch_all_records(collection_name, limit)
        return {"status": "success", "data": records}
    except Exception as err:
        logger.error('Error while fetching the records from the collection:', str(err))
        return responseHandler.failure_response(
            str(err),
            500
        )

@mod_rag.route("/api/v1/chat", methods=['POST'])
@token_required
def query_documents():
    try:
        request_data = request.json
        messages = request_data['messages']

        current_query = messages[-1]

        if current_query["role"] != 'user':
            return responseHandler.failure_response(
                "user message does not exists.",
                400
            )

        # Build the previous chat context
        context = ''
        for message in messages[:-1]:
            context = context + message['role'] + ':\n'
            context = context + message['content'] + '\n\n'

        answer, links = generate_query_response(context, current_query['content'])

        response = {
            "response": [
                {
                    "answer": {
                        "content": answer,
                        "role": "assistant"
                    },
                    "citation": links
                }
            ]
        }

        return response

    except Exception as err:
        logger.error('Error while generating the response to the given query:', str(err))
        return responseHandler.failure_response(
            str(err),
            500
        )

# Endpoint to authenticate and issue a token
@mod_rag.route('api/v1/login', methods=['POST'])
def login():
    # In a real-world scenario, you'd check user credentials from a database
    data = request.json
    username = data.get('username')
    password = data.get('password')

    # Simple mock user validation (replace with your real user validation)
    if username == 'admin' and password == 'password':
        # Create the payload for the JWT token
        payload = {
            'user': username,
            'exp': datetime.now(timezone.utc) + timedelta(hours=1)  # Token expires in 1 hour
        }

        # Create the JWT token
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials!'}), 401
