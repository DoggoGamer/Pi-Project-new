import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from playsound import playsound
import speech_recognition as sr
import time

def listen_for_wake_word():
    recognizer = sr.Recognizer()
    
    while True:
        with sr.Microphone() as source:
            print("Listening for 'Computer'...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=1)
                text = recognizer.recognize_google(audio).lower()
                if "computer" in text:
                    print("Wake word detected! Listening for your question...")
                    with sr.Microphone() as question_source:
                        recognizer.adjust_for_ambient_noise(question_source)
                        question_audio = recognizer.listen(question_source)
                        question = recognizer.recognize_google(question_audio)
                        print(question)
                        return question
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                print("Could not request results; check your internet connection")
                continue

def append_to_history(role, content):
    with open("history.txt", "a") as history_file:
        history_file.write(f"{role}: {content}\n")

def get_conversation_history():
    if not os.path.exists("history.txt"):
        return []
    with open("history.txt", "r") as history_file:
        lines = history_file.readlines()
    conversation = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ": " in line:
            try:
                role, content = line.split(": ", 1)
                conversation.append({"role": "system" if role == "system" else "user", "content": content.strip()})
            except Exception as e:
                print(f"Error processing line: {line} - {e}")
    return conversation

# Get the user's question through voice
user_question = listen_for_wake_word()
append_to_history("user", user_question)

load_dotenv()  # Load environment variables from .env file

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

conversation_history = get_conversation_history()
conversation_history.append({"role": "user", "content": user_question})

response = client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=100,
    messages=conversation_history
)

assistant_response = response.choices[0].message.content
append_to_history("system", assistant_response)

# print(response)

speech_file_path = Path(__file__).parent / "speech.mp3"
response2 = client.audio.speech.create(
  model="tts-1",
  voice="nova",
  input=assistant_response
)

# Save the audio file
with open(speech_file_path, 'wb') as file:
    for chunk in response2.iter_bytes():
        file.write(chunk)

# Load and play the audio file
playsound(speech_file_path)