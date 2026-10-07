import glob
import logging
import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import AzureSearch
from langchain_openai import AzureOpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(override=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("indexer")


def index_docs():
    """Read PDFs from backend/data and put their chunks into Azure AI Search."""
    data_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../data")
    )

    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    )

    vector_store = AzureSearch(
        azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
        index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
        embedding_function=embeddings.embed_query,
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    all_documents = []

    for pdf_path in glob.glob(os.path.join(data_folder, "*.pdf")):
        try:
            logger.info("Reading %s", os.path.basename(pdf_path))

            documents = PyPDFLoader(pdf_path).load()
            chunks = splitter.split_documents(documents)

            for chunk in chunks:
                chunk.metadata["source"] = os.path.basename(pdf_path)

            all_documents.extend(chunks)
            logger.info("Created %s chunks", len(chunks))

        except Exception as error:
            logger.error("Could not process %s: %s", pdf_path, error)

    if not all_documents:
        logger.warning("No PDF documents were found.")
        return

    vector_store.add_documents(documents=all_documents)

    logger.info(
        "Indexing complete. Added %s chunks to Azure AI Search.",
        len(all_documents),
    )


if __name__ == "__main__":
    index_docs()
