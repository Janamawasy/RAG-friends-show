from utils.rag_utils import extract_text_from_pdf
import os
from dotenv import load_dotenv
from langchain.docstore.document import Document
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ai21 import AI21Embeddings
from langchain_community.vectorstores import FAISS
from langchain_ai21 import AI21LLM
from fastapi import HTTPException
import logging
import json


# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()


class RAG():
    def __init__(self):
        try:
            self.pdf_paths = ["data/Friends_Transcript.pdf"]
            self.__api_key = os.getenv("AI21_API_KEY")
            self.__config = self.__load_config()

            if self.__config['vectorstore_created'] == 1:
                print('vectorstore is 1')
                self.__faiss_index = self.__load_vectorstore()

            else:
                print('vectorstore is 0')
                self.__all_texts = self.__upload_data()
                self.__documents = self.__documenting_text()
                self.__splits = self.__split_documents()
                self.__faiss_index = self.__embed_vectorStore()

            self.__retriever = self.__retrieve()
            self.__rag_chain = self.__create_chain()
        except Exception as e:
            logging.error(f"Error occurred while initializing the RAG: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error occurred while initializing the RAG: {str(e)}")

    def __load_config(self):
        """
        Load the configuration file to check if vectorstore is already created.
        """
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logging.error(f"Error occurred while loading the config: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error occurred while loading the config: {str(e)}")

    def __upload_data(self):
        """
        Load text data from PDF files.
        """
        try:
            all_texts = []
            for pdf_path in self.pdf_paths:
                text = extract_text_from_pdf(pdf_path)
                all_texts.append(text)
            return all_texts
        except Exception as e:
            logging.error(f"Error occurred while uploading data: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error occurred while uploading data: {str(e)}")

    def __documenting_text(self):
        """
        Convert text data into Document objects.
        """
        try:
            documents = [Document(page_content=text) for text in self.__all_texts]
            return documents
        except Exception as e:
            logging.error(f"Error occurred while documenting text: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error occurred while documenting text: {str(e)}")

    def __split_documents(self):
        """
        Split documents into smaller chunks for processing.
        """
        try:
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            splits = text_splitter.split_documents(self.__documents)
            return splits
        except Exception as e:
            logging.error(f"Error occurred while splitting documents: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error occurred while splitting documents: {str(e)}")

    def __embed_vectorStore(self):
        """
        embedding splits using ai21 embedding model and creating a FAISS vector store for the embedded documents.
        """
        try:
            embeddings_model = AI21Embeddings(api_key=self.__api_key)
            faiss_index = FAISS.from_texts([doc.page_content for doc in self.__splits], embeddings_model)
            # with open('faiss_index.pkl', 'wb') as f:
            #     pickle.dump(faiss_index, f)
            # faiss.write_index(faiss_index.index, 'faiss_index.bin')
            faiss_index.save_local("faiss_index")

            config = self.__load_config()
            config['vectorstore_created'] = 1
            with open('config.json', 'w') as f:
                json.dump(config, f)

            logging.info("Created and saved new FAISS vector store + updated config file.")
            return faiss_index
        except Exception as e:
            logging.error(f"Error occurred while embedding and vector storing: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error occurred while embedding and vector storing: {str(e)}")

    def __load_vectorstore(self):
        try:
            embeddings_model = AI21Embeddings(api_key=self.__api_key)
            faiss_index = FAISS.load_local("faiss_index", embeddings_model, allow_dangerous_deserialization=True)

            logging.info("FAISS index loaded successfully")
            return faiss_index
        except Exception as e:
            logging.error(f"Error occurred while loading the FAISS index: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error occurred while loading the FAISS index: {str(e)}")

    def __retrieve(self):
        """
        Initialize the retriever for the FAISS index
        """
        try:
            retriever = self.__faiss_index.as_retriever()
            return retriever
        except Exception as e:
            logging.error(f"Error occurred while initializing retriever: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error occurred while initializing retriever: {str(e)}")

    def __create_chain(self):
        """
        Create the RAG chain with the appropriate prompt.
        """
        try:
            system_prompt = (
                "You are an assistant for questions related to Friends TV show Only!"
                "Please answer questions within this domain."

                "You are an assistant for question-answering tasks. "
                "Use the following pieces of retrieved context to answer the question."
                "If you don't know the answer, or the question not related to the context return this answer: your question is not related to the context or could not be answered."

                "context: {context}"

                "question: {input}"
            )

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{input}")
                ]
            )
            llm = AI21LLM(model="j2-ultra", max_tokens=256)
            question_answer_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
            rag_chain = create_retrieval_chain(self.__retriever, question_answer_chain)
            return rag_chain
        except Exception as e:
            logging.error(f"Error occurred while creating the chain: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error occurred while creating the chain: {str(e)}")

    def submit_question(self, question):
        """Submit a question to the RAG chain and return the answer"""
        try:
            if question:
                response = self.__rag_chain.invoke({'input': question})
                return response['answer']
            else:
                raise Exception("Question is required")
        except Exception as e:
            logging.error(f"Error occurred while submitting question: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error occurred while submitting question: {str(e)}")