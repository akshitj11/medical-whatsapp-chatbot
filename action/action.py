# ===============================================================================
# PERMANENT FIX for SQLite issue in Codespaces
# ===============================================================================
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
# ===============================================================================

import os
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from langchain.vectorstores import Chroma
# --- VERTEX AI FIX: Import Vertex AI classes for embeddings and LLMs ---
from langchain.embeddings import VertexAIEmbeddings
from langchain.llms import VertexAI
from langchain.chains import RetrievalQA

# --- Configuration ---
VECTOR_STORE_DIRECTORY = "db"

class ActionQueryRag(Action):
    def __init__(self):
        super().__init__()
        # --- VERTEX AI FIX: Use VertexAIEmbeddings ---
        self.embeddings = VertexAIEmbeddings()

        if not os.path.exists(VECTOR_STORE_DIRECTORY):
             raise FileNotFoundError(f"Vector store not found. Run ingest_docs.py first.")
        self.vector_store = Chroma(
            persist_directory=VECTOR_STORE_DIRECTORY,
            embedding_function=self.embeddings
        )

        # --- VERTEX AI FIX: Use VertexAI LLM ---
        self.llm = VertexAI(temperature=0.7)

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_ retriever(),
            return_source_documents=True
        )
        print("RAG Action server (Vertex AI) initialized successfully.")

    def name(self) -> Text:
        return "action_query_rag"

    async def run(self, dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_question = tracker.latest_message.get('text')
        print(f"Received question for RAG: {user_question}")

        if not user_question:
            dispatcher.utter_message(text="I'm sorry, I didn't get a question.")
            return []

        try:
            response = self.qa_chain({"query": user_question})
            answer = response.get("result", "I couldn't find an answer.")
            dispatcher.utter_message(text=answer)
        except Exception as e:
            print(f"An error occurred during RAG query: {e}")
            dispatcher.utter_message(text="Sorry, an error occurred.")

        return []

    

