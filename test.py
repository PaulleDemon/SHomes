import os
import requests
import pyttsx3
import json
from dotenv import load_dotenv

load_dotenv()


engine = pyttsx3.init()

voices = engine.getProperty('voices')
print("Voices: ", [(index, x.id, x.name, x.gender)  for index, x in enumerate(voices)])
# engine.setProperty('voice', voices[16].id)  

engine.setProperty('voice', 'english+f1')
# res = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={ os.getenv('newsAPI')}&pageSize=3")
pyttsx3.speak("Reading top headlines f1")

engine.setProperty('voice', 'english+f2')
pyttsx3.speak("Reading top headlines f2")

engine.setProperty('voice', 'english+f3')
pyttsx3.speak("Reading top headlines f3")

engine.setProperty('voice', 'english+f4')
pyttsx3.speak("Reading top headlines f4")



# for x in res.json()["articles"]:
#     print(x["title"])
#     pyttsx3.speak(x["title"])

# engine.runAndWait()