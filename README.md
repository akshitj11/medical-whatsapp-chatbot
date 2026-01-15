 # 🏥 Mediaware: AI-Powered Medical Awareness Chatbot

**Mediaware** is a sophisticated, multilingual, and voice-enabled medical assistant.  
It leverages a **Retrieval-Augmented Generation (RAG)** pipeline to provide highly accurate, fact-based answers derived directly from your **custom library of medical PDF documents**.

---

## 🏗️ Architecture & Framework

The project follows a **Decoupled Microservice Architecture**, ensuring each component handles a specific part of the conversation lifecycle.

---

## 🔄 Data Flow

1. **Frontend (UI)**  
   - Captures text or voice input in any Indian language

2. **Webhook Server (Flask)** – *Traffic Controller*  
   - Handles Speech-to-Text transcription  
   - Translates user input into English using **Google Cloud APIs**

3. **Rasa Server** – *The Brain*  
   - Determines user intent  
   - Triggers a custom action for medical queries

4. **Rasa Action Server (RAG)** – *Knowledge Expert*  
   - **Retrieval**: Searches the ChromaDB vector store for relevant document chunks  
   - **Augmentation**: Combines user query with retrieved context  
   - **Generation**: Sends prompt to **Google Vertex AI (LLM)** for grounded responses

5. **Response Flow**  
   - Translates the answer back to the user’s native language  
   - Delivers output via **text and voice**

---

## 📂 Project Structure




<img width="926" height="448" alt="image" src="https://github.com/user-attachments/assets/5bf65cd0-6128-430d-8c70-e2f7457516e5" />





