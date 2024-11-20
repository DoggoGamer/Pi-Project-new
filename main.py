import os
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path
from playsound import playsound
import speech_recognition as sr
import time


recognizer = sr.Recognizer()


def listen_for_input():
#    recognizer = sr.Recognizer()
    
    # Listen for the wake word "computer" once
    with sr.Microphone() as source:
        print("Listening for wake word 'computer'...")
        recognizer.adjust_for_ambient_noise(source)
        while True:
            try:
                audio = recognizer.listen(source, timeout=1)
                text = recognizer.recognize_google(audio).lower()
                if "computer" in text:
                    print("Wake word detected. Listening for input...")
                    break
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                print("Could not request results; check your internet connection")
                continue

    # Continuously listen for input until "bye computer" is detected
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise again
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio).lower()
                if "bye computer" in text:
                    print("Goodbye!")
                    return None
                print(f"Received input: {text}")
                return text
            except sr.WaitTimeoutError:
                # If no input is detected within 5 seconds, continue listening
                print("No input detected. Continuing to listen for input.")
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

# Loop to continuously listen for input and process questions
while True:
    # Get the user's input through voice
    user_input = listen_for_input()
    if user_input is None:
        break
    append_to_history("user", user_input)

    load_dotenv()  # Load environment variables from .env file

    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    conversation_history = get_conversation_history()
    conversation_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=100,
        messages=conversation_history
    )

    assistant_response = response.choices[0].message.content
    append_to_history("system", assistant_response)

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

    # Start a 5-second timer to wait for more input
    print("Waiting for more input...")
    time.sleep(5)

    # Check for more input
#    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio).lower()
            if "bye computer" in text:
                print("Goodbye!")
                break
            print(f"Received input: {text}")
            append_to_history("user", text)
            # Continue processing the input as before
        except sr.WaitTimeoutError:
            print("No input detected. Returning to wake word listening.")
            continue
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            print("Could not request results; check your internet connection")
            continue
    