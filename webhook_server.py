import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests as http_requests

# --- Google Cloud API Initialization ---
# This server now requires both Translate and Speech-to-Text APIs.
# Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set.
try:
    from google.cloud import translate_v2 as translate
    from google.cloud import speech
    translate_client = translate.Client()
    speech_client = speech.SpeechClient()
    print("Google Translate and Speech-to-Text clients initialized successfully.")
except Exception as e:
    print("Could not initialize Google Cloud clients.")
    print("Please ensure you have installed 'google-cloud-translate' and 'google-cloud-speech'.")
    print(f"Error: {e}")
    translate_client = None
    speech_client = None

# --- Configuration ---
RASA_SERVER_URL = "http://localhost:5005/webhooks/rest/webhook"
# A list of common Indian language codes for more accurate speech recognition.
# You can add more from the Google Cloud documentation.
INDIAN_LANGUAGE_CODES = ["en-IN", "hi-IN", "bn-IN", "te-IN", "mr-IN", "ta-IN", "gu-IN", "kn-IN", "ml-IN", "pa-IN"]


app = Flask(__name__)
CORS(app)

# --- Helper Functions ---
def transcribe_audio(audio_content):
    """Transcribes audio content using Google Speech-to-Text."""
    if not speech_client:
        return None, "en-US" # Fallback if client is not available

    try:
        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS, # Common format from browsers
            sample_rate_hertz=48000, # Common sample rate for web audio
            enable_automatic_punctuation=True,
            language_code="en-US", # A base language
            alternative_language_codes=INDIAN_LANGUAGE_CODES # More importantly, provide alternatives
        )

        print("Sending audio to Google Speech-to-Text API...")
        response = speech_client.recognize(config=config, audio=audio)
        
        if response.results:
            transcript = response.results[0].alternatives[0].transcript
            language_code = response.results[0].language_code
            print(f"Transcription successful. Detected language: {language_code}")
            return transcript, language_code
        else:
            print("Speech-to-Text API returned no results.")
            return None, "en-US"
            
    except Exception as e:
        print(f"Error during transcription: {e}")
        return None, "en-US"

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Unified webhook to handle both text and voice messages.
    It checks the content type to decide how to process the request.
    """
    sender_id = request.form.get("sender", "default-user")
    
    # --- Voice Processing ---
    if 'audio' in request.files:
        print("\n--- New VOICE Request ---")
        audio_file = request.files['audio']
        audio_content = audio_file.read()

        user_message, original_lang_code = transcribe_audio(audio_content)
        if not user_message:
            return jsonify({"response": "Sorry, I could not understand the audio. Please try again."}), 400
        original_lang = original_lang_code.split('-')[0] # Get base language e.g., 'hi' from 'hi-IN'

    # --- Text Processing ---
    else:
        print("\n--- New TEXT Request ---")
        data = request.get_json()
        user_message = data.get("message")
        sender_id = data.get("sender")
        if not user_message:
            return jsonify({"error": "Missing message"}), 400
        # For text, we detect language during translation
        original_lang = None

    print(f"Original message from '{sender_id}': {user_message}")

    # 1. Translate user message to English (if not already)
    if translate_client:
        translation_result = translate_client.detect_language(user_message)
        detected_lang = translation_result['language']
        if not original_lang:
            original_lang = detected_lang

        if detected_lang != 'en':
            print(f"Translating from '{detected_lang}' to English...")
            translation_result = translate_client.translate(user_message, target_language='en')
            english_message = translation_result['translatedText']
        else:
            english_message = user_message
    else: # Fallback if no translate client
        english_message = user_message
        original_lang = 'en'

    print(f"Message to Rasa (English): {english_message}")

    # 2. Send to Rasa
    rasa_payload = {"sender": sender_id, "message": english_message}
    try:
        rasa_response = http_requests.post(RASA_SERVER_URL, json=rasa_payload)
        rasa_response.raise_for_status()
        rasa_messages = rasa_response.json()
    except http_requests.exceptions.RequestException as e:
        print(f"Error connecting to Rasa server: {e}")
        return jsonify({"error": "Could not connect to the chatbot engine."}), 500

    # 3. Process and translate Rasa's response back
    if rasa_messages:
        bot_response_english = rasa_messages[0].get("text", "Sorry, I don't have an answer for that.")
        print(f"Rasa response (English): {bot_response_english}")

        if translate_client and original_lang != 'en':
            print(f"Translating response back to '{original_lang}'...")
            translation_result = translate_client.translate(bot_response_english, target_language=original_lang)
            final_response = translation_result['translatedText']
        else:
            final_response = bot_response_english
    else:
        final_response = "I'm sorry, I didn't get a response. Please try again."
    
    print(f"Final response (for lang '{original_lang}'): {final_response}")

    return jsonify({"response": final_response, "language": original_lang})


if __name__ == "__main__":
    print("Starting multilingual VOICE and TEXT webhook server on http://localhost:5000")
    # Note: Flask's development server is not suitable for production.
    app.run(port=5000)

