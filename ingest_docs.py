# ===============================================================================
# PERMANENT FIX for SQLite issue in Codespaces
# ===============================================================================
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ===============================================================================

import os
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
# --- VERTEX AI FIX: Import the Vertex AI embedding class ---
from langchain.embeddings import VertexAIEmbeddings
from tqdm import tqdm

# --- Configuration ---
DOCS_DIRECTORY = "docs"
VECTOR_STORE_DIRECTORY = "db"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

def ingest_documents():
    """
    Ingests PDF documents, splits them, generates embeddings using the Vertex
    AI API, and stores them in a Chroma vector store.
    """
    print(f"Loading documents from the '{DOCS_DIRECTORY}' directory...")
    document_paths = [os.path.join(DOCS_DIRECTORY, filename) for filename in os.listdir(DOCS_DIRECTORY) if filename.endswith(".pdf")]

    all_docs = []
    for doc_path in tqdm(document_paths, desc="Processing PDFs"):
        try:
            loader = PyMuPDFLoader(doc_path)
            all_docs.extend(loader.load())
        except Exception as e:
            print(f"\nError processing file {doc_path}: {e}")
            continue

    if not all_docs:
        print("No documents were loaded. Please check the 'docs' directory.")
        return

    print(f"Loaded {len(all_docs)} document pages.")

    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    split_docs = text_splitter.split_documents(all_docs)
    print(f"Split documents into {len(split_docs)} chunks.")

    print("Creating vector store with Vertex AI embeddings... (This may take a while)")
    # --- VERTEX AI FIX: Use VertexAIEmbeddings ---
    # It automatically authenticates using the GOOGLE_APPLICATION_CREDENTIALS
    embeddings = VertexAIEmbeddings()

    # Create the Chroma vector store
    vector_store = Chroma.from_documents(
        documents=split_docs,
        embedding=embeddings,
        persist_directory=VECTOR_STORE_DIRECTORY
    )

    print(f"\nIngestion complete!")
    print(f"Vector store created using Vertex AI embeddings in '{VECTOR_STORE_DIRECTORY}'.")

if __name__ == "__main__":
    ingest_documents()

