import os
from openai import OpenAI
from pathlib import Path
from playsound import playsound


client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

response = client.chat.completions.create(
    model="gpt-4o-mini",
    max_tokens=100,
    messages=[{"role": "system", "content": "You are a helpful assistant. Limit your response to 100 tokens."}, {"role": "user", "content": "Where is the nearest star?"}]
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