# RAG API Service

This project is a RESTful API built with Flask to perform various operations for a Retrieval-Augmented Generation (RAG) system. The functionalities include user authentication, URL indexing, collection creation, fetching records, and querying documents with chat history.

---

## Features

- **User Authentication**: Issue and verify JWT tokens for API access.
- **Health Check Endpoint**: Verifies the API service is running.
- **URL Indexing**: Processes and indexes content from provided URLs into a vector database.
- **Collection Management**: Create collections for storing document embeddings.
- **Fetch Records**: Retrieve stored records from a collection.
- **Chat Interface**: Simulates a chatbot with document query capabilities, including maintaining context and providing citations.

---

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- Flask and related dependencies
- A Vector Database (Open-sourced Qdrant in this case)
- `pip` for package installation
- A valid `SECRET_KEY` for JWT generation

---

### 2. Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/imVParashar/rag_api.git

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   
4. **Set up the environment variables**:

   Create a .env file in the project root and add the following:
   ```bash
   FIRECRAWL_API_KEY = "your-secret-api-key"
   OPENAI_API_KEY = 'your-secret-api-key'
   SECRET_KEY = "secret-for-jwt-encoding"
   
5. **Run the Flask server**:
   ```bash
   python3 main.py


## API Documentation

This document provides a comprehensive overview of the API functionalities for our service.

### Authentication

The `/rag/api/v1/login` endpoint allows users to authenticate and obtain a JWT token for subsequent API calls.

#### Login

**Endpoint:**  POST /rag/api/v1/login

**Headers:**  None

**Request Body (JSON):**

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

**Response (JSON):**

Upon successful login, the response contains a JWT token:

```json
{
  "token": "your-jwt-token"
}
```

**Note:** Replace `your_username` and `your_password` with your actual credentials.

### Health Check

The `/rag/api/v1/health` endpoint verifies if the API service is running.

#### Health Check

**Endpoint:** GET /rag/api/v1/health

**Headers:**  Requires a valid JWT token in the `Authorization` header:

```json
{
  "Authorization": "Bearer your-jwt-token"
}
```

**Response (JSON):**

A successful response indicates the API is healthy:

```json
{
  "message": "Health check successful",
  "status_code": 200
}
```

### Index URLs

The `/rag/api/v1/index` endpoint processes and indexes content from provided URLs into the vector database.

#### Index URLs

**Endpoint:** POST /rag/api/v1/index

**Headers:**  Requires a valid JWT token in the `Authorization` header:

```json
{
  "Authorization": "Bearer your-jwt-token"
}
```

**Request Body (JSON):**

Provide a list of URLs to be indexed:

```json
{
  "url": ["https://example.com/article1", "https://example.com/article2"]
}
```

**Response (JSON):**

The response indicates success and lists indexed and failed URLs (if any):

```json
{
  "status": "success",
  "indexed_url": ["https://example.com/article1"],
  "failed_url": ["https://example.com/article2"]  // Optional if indexing fails
}
```

### Create Collection

The `/rag/api/v1/create_collection` endpoint creates a new collection for storing document embeddings in the vector database.

#### Create Collection

**Endpoint:** POST /rag/api/v1/create_collection

**Headers:**  Requires a valid JWT token in the `Authorization` header:

```json
{
  "Authorization": "Bearer your-jwt-token"
}
```

**Request Body (JSON):**

Specify the desired collection name:

```json
{
  "collection_name": "example_collection"
}
```

**Response (JSON):**

A successful response confirms the collection creation:

```json
{
  "status": "Collection 'example_collection' created successfully."
}
```

### Fetch Records

The `/rag/api/v1/fetch_records` endpoint retrieves documents from a specified collection.

#### Fetch Records

**Endpoint:** POST /rag/api/v1/fetch_records

**Headers:**  Requires a valid JWT token in the `Authorization` header:

```json
{
  "Authorization": "Bearer your-jwt-token"
}
```

**Request Body (JSON):**

Indicate the collection name and optional limit for retrieved documents:

```json
{
  "collection_name": "example_collection",
  "limit": 10  // Optional, defaults to all documents
}
```

**Response (JSON):**

The response includes a status message and retrieved document data:

```json
{
  "status": "success",
  "data": [...]  // Array containing document information
}
```

### Chat with Documents

The `/rag/api/v1/chat` endpoint enables users to interact with documents through a chat interface. This functionality maintains context across messages and retrieves answers with citations.

#### Chat with Documents

**Endpoint:** POST /rag/api/v1/chat

**Headers:**  Requires a valid JWT token in the `Authorization` header:

```json
{
  "Authorization": "Bearer your-jwt-token"
}
```

**Request Body (JSON):**

Provide an array of message objects with roles (`user` or `assistant`) and content:

**Request Body (JSON):**

```json
{
    "messages": [
        {"role": "user", "content": "What is COLBERT"},
        {"role": "assistant", "content": "ColBERT stands for Contextualized Late Interaction over BERT. It is a model developed at Stanford University that enhances information retrieval by using a late interaction mechanism, allowing for efficient and precise retrieval of documents by processing queries and documents separately until the final stages. The model has two versions: ColBERT and ColBERTv2, with the latter introducing improvements like denoised supervision and residual compression."},
        {"role": "user", "content": "Why is it required?"}
    ]
}
```

**Response (JSON):**

The response includes an answer and citations:

```json
{
    "response": [
        {
            "answer": {
                "content": "ColBERT is required to enhance the efficiency and effectiveness of information retrieval by leveraging a late interaction mechanism. This allows for significant reductions in computational costs and latency while maintaining high retrieval performance, making it suitable for real-world applications with large document collections.",
                "role": "assistant"
            },
            "citation": [
                "https://jina.ai/news/what-is-colbert-and-late-interaction-and-why-they-matter-in-search/"
            ]
        }
    ]
}
```

### Logging and Error Handling

* **Logging:** All logs are maintained using the logger utility. Log levels and file configurations can be adjusted in `app/utilities/logger.py`.
* **Error Handling:** The application uses a standardized error response format.

**Example Error Response:**

```json
{
  "message": "Invalid token.",
  "status_code": 401
}
```