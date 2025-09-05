 Key Features
Multilingual Support: Engages users in a wide range of Indian languages through real-time translation.

Retrieval-Augmented Generation (RAG): Ensures answers are accurate and grounded in the provided medical documents, minimizing hallucinations.

Custom Knowledge Base: Easily trainable by simply adding PDF files to a directory.

Modern Web Interface: A warm and comforting user interface inspired by the Gemini aesthetic.

🏗️ Project Framework & Architecture
This project is built on a decoupled, microservice-style architecture. This design separates the user interface, language processing, and core conversational logic, making the system scalable and easy to maintain.

The data flows through the system as follows:

Frontend: The user interacts with the web interface. Voice or text input is captured and sent to the Webhook Server.

Webhook Server (Flask): This Python server acts as the central hub.

It receives the user's query.

If the input is audio, it uses the Google Speech-to-Text API to transcribe it.

It uses the Google Translate API to translate the user's query into English.

It forwards the English text to the Rasa Server.

Rasa Server: This is the core conversational brain. It processes the English text, identifies the user's intent (e.g., asking a question), and determines the next action.

Rasa Action Server: When a question is detected, the Rasa Server calls this custom server. The action server executes the RAG pipeline:

It queries the ChromaDB vector store to find the most relevant text chunks from the original PDF documents.

It combines the user's question with this retrieved context.

It sends the combined prompt to Google's Vertex AI language model to generate a factual answer.

Response Flow: The generated answer travels back through the same chain. The Webhook Server translates the English response back into the user's original language and sends it to the frontend, where it is displayed and spoken aloud.

🛠️ Technology Stack
This project integrates a powerful set of modern AI and web development technologies.

AI & Machine Learning
Rasa: The primary open-source framework for building the conversational AI. It manages dialogue flow and natural language understanding (NLU).

LangChain: The core library for orchestrating the RAG pipeline, connecting the language model, vector database, and document loaders.

Google Vertex AI: Provides the powerful Large Language Models (LLMs) used for generating answers and creating text embeddings.

TensorFlow: The underlying machine learning library used by Rasa to train its models.

Backend & Servers
Python: The exclusive programming language for the entire backend logic.

Flask: A lightweight Python web framework used for the webhook_server.py, which handles API requests from the frontend.

Data & Storage
ChromaDB: An open-source vector database for storing document embeddings and enabling efficient similarity search for the RAG pipeline.

Frontend (User Interface)
HTML5: The structure of the web-based chat interface.

Tailwind CSS: A utility-first CSS framework for creating the modern, responsive design.

Vanilla JavaScript: Handles all client-side logic, including DOM manipulation, voice recording via the Web Speech API, and communication with the backend.

Cloud Services & APIs
Google Cloud Platform (GCP):

Translation API: Provides real-time translation for multilingual conversations.

Speech-to-Text API: Transcribes user voice input into text.

Development Environment
GitHub Codespaces: The cloud-based development environment used to build, test, and run the application, ensuring a consistent and dependency-free setup.

Git & Git LFS: Version control for managing the source code and tracking large model files.



<img width="1920" height="1080" alt="Screenshot (371)" src="https://github.com/user-attachments/assets/ada5e730-9bdc-4a25-b1c0-d626fceb1136" />


main/
├── actions/            # Custom Python code for the Rasa Action Server (RAG pipeline).
├── data/               # Training data for Rasa (NLU, stories).
├── docs/               # Your custom knowledge base (add your PDFs here).
│
├── config.yml          # Rasa NLU pipeline and Core policy configuration.
├── domain.yml          # The chatbot's world: all known intents and actions.
├── endpoints.yml       # Connects the Rasa Server to the Action Server.
├── index.html          # The complete frontend user interface.
├── ingest_docs.py      # Script to train the RAG system from your PDFs.
├── requirements.txt    # All required Python libraries.
└── webhook_server.py   # Flask server for language processing and API handling.



