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
            print("Listening for 'Hey Ali'...")
            recognizer.adjust_for_ambient_noise(source)
            try:
                audio = recognizer.listen(source, timeout=1)
                text = recognizer.recognize_google(audio).lower()
                if "hey ali" in text:
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

# Get the user's question through voice
user_question = listen_for_wake_word()

load_dotenv()  # Load environment variables from .env file

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=100,
    messages=[{"role": "system", "content": "You are a helpful assistant. Limit your response to 100 tokens."}, {"role": "user", "content": user_question}]
)

# print(response)

speech_file_path = Path(__file__).parent / "speech.mp3"
response2 = client.audio.speech.create(
  model="tts-1",
  voice="nova",
  input=response.choices[0].message.content
)

# Save the audio file
with open(speech_file_path, 'wb') as file:
    for chunk in response2.iter_bytes():
        file.write(chunk)

# Load and play the audio file
playsound(speech_file_path)