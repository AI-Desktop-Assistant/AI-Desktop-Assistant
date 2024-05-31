import speech_recognition as sr
import pyttsx3


recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

output = "hi im", recognizer

def speak(text):
    print("Saying: ", text)
    tts_engine.say(text)
    tts_engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Say something")
        audio = recognizer.listen(source, 10, 2)
        try:
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
        return text
