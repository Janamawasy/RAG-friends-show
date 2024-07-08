# Friends TV show QA

This project is a Question-Answering (QA) system built using Retrieval-Augmented Generation (RAG) techniques. It allows users to ask questions based on the content of provided PDFs. The application consists of a backend server using FastAPI and a frontend UI built with Streamlit.

## Features
- Extracts and processes text from PDF.
- Uses a Vector Store to store and retrieve relevant document chunks.
- Answers questions based on the content of the provided PDF.
- Displays answers in green and error messages in red in the UI.

## Prerequisites

- Docker
- Python 3.12
- Pip
- Git
- Langchain

## Install Dependencies
Create and activate a virtual environment:

```
  python -m venv venv
  source venv/bin/activate  # On Windows use `venv\Scripts\activate`
  
  pip install -r requirements.txt
```

## Environment Variables
Create a .env file in the root directory of the project and add your API key and server URL,
api_key for [AI21 embedding mpdel](https://studio.ai21.com/account/api-key?source=docs).

```
  AI21_API_KEY=your_ai21_api_key
  SERVER_URL=http://localhost:8000
```

## Running the Project
if its the first time running the project make sure to set the 'vectorstore_created' value to 0 in the config.json file.
otherwise, set it to 1 to use the pre-built VectorStore index.

Run the FastAPI server:
```
  uvicorn server:app --host 127.0.0.1 --port 8000
```
Run the Streamlit UI - streamlit runs on port 8501 by default:
```
  streamlit run gui.py
```

## Project Structure
```
  ├── data
  │   ├── Friends_Transcript.pdf
  ├── faisis_index
  │   ├── index.faisis
  │   ├── index.pkl
  ├── utils
  │   └── rag_utils.py
  ├── gui.py
  ├── server.py
  ├── rag.py
  ├── requirements.txt
  ├── README.md
  ├── config.json
  └── .env
```

## Explanation of Main Files
  - data/: Folder containing the PDF documents.
  - utils/rag_utils.py: Contains utility functions for extracting text from PDFs.
  - gui.py: Contains the Streamlit UI code.
  - server.py: Contains the FastAPI server code.
  - rag.py: The RAG class contains all the logic for document processing, embedding, vectorstore, and question answering.
  - requirements.txt: List of dependencies required for the project.
  - README.md: This file, containing project instructions and information.
  - config.json: Configuration file for VectorStore, if it already created and stored 'vectorstore_created' value is 1, if not its 0.
  - .env: Environment variables file.
  - faisis_index/: Folder containing the VectorStore index files.



