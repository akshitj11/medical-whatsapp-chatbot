import os
from tqdm import tqdm
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# --- Configuration ---
# IMPORTANT: Set your Google API Key here
# You can get a key from https://aistudio.google.com/app/apikey
GOOGLE_API_KEY = "AIzaSyBWGBe_Ka_6nwRdf-8wwrHqJpQIBfRyaZw"

DOCS_DIR = "docs" # Folder where your PDFs are stored
DB_DIR = "db" # Folder where the vector database will be stored
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def main():
    """
    Main function to ingest documents into the Chroma vector store.
    1. Checks for GOOGLE_API_KEY.
    2. Loads PDF documents from the specified directory.
    3. Splits the documents into manageable chunks.
    4. Creates embeddings for the chunks using Google's model.
    5. Stores the chunks and their embeddings in a Chroma vector database.
    """
    print("--- Starting Document Ingestion ---")

    # 1. API Key Check
    if not GOOGLE_API_KEY or GOOGLE_API_KEY == "AIzaSyBWGBe_Ka_6nwRdf-8wwrHqJpQIBfRyaZw":
        print("ERROR: GOOGLE_API_KEY is not set. Please set it in ingest_docs.py")
        return

    # Check if the docs directory exists
    if not os.path.exists(DOCS_DIR):
        print(f"ERROR: Directory '{DOCS_DIR}' not found. Please create it and add your PDF files.")
        return

    # 2. Load Documents
    documents = []
    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in the '{DOCS_DIR}' directory.")
        return

    print(f"Found {len(pdf_files)} PDF(s) to process...")
    for pdf_file in tqdm(pdf_files, desc="Loading PDFs"):
        file_path = os.path.join(DOCS_DIR, pdf_file)
        loader = PyMuPDFLoader(file_path)
        documents.extend(loader.load())
    print(f"Successfully loaded {len(documents)} pages from all PDFs.")

    # 3. Split Documents
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    texts = text_splitter.split_documents(documents)
    print(f"Created {len(texts)} text chunks.")

    # 4. Create Embeddings
    print("Initializing Google Generative AI Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY)

    # 5. Store in Chroma
    print(f"Creating and persisting vector store in '{DB_DIR}'...")
    # This command creates the database, embeds the documents, and saves it to disk.
    db = Chroma.from_documents(texts, embeddings, persist_directory=DB_DIR)
    
    # Force a persist to ensure it's written to disk
    db.persist()
    db = None

    print("--- Document Ingestion Complete ---")
    print(f"Vector store has been successfully created and saved in the '{DB_DIR}' directory.")

if __name__ == "__main__":
    main()
