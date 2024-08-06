import speech_recognition as sr
import pyttsx3
from google.cloud import texttospeech
from config_socketio import get_app_socket
import pygame
import io
import os
import time

wake_word = 'hey computer'
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
tts_engine.setProperty('volume', 0.5)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcp_creds\\ai-desktop-assistant-425120-fc21e54bf79d.json'
client = texttospeech.TextToSpeechClient()
pygame.mixer.init(frequency=24000)
pygame.mixer.music.set_volume(0.1)

is_audio = True

def google_tts(text):
    print(f'Returning chat: {text}')
    send_chat('assistant', text)
    if is_audio:
        print("playing google")
        input_text = texttospeech.SynthesisInput(text=text)
        print('Synthesizing input')
        # selected_voice = get_selected_voice()
        print('Selecting Voice')
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Wavenet-B",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )
        print('Setting Audio config')
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            sample_rate_hertz=24000
        )
        print('Synthesizing Speech')
        response = client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config
        )
        print('Loading Synthesized Speech to PyGame')
        pygame.mixer.music.load(io.BytesIO(response.audio_content))

        print("Saying: ", text)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    
def py_tts(text):
    print("Saying: ", text)
    tts_engine.say(text)
    tts_engine.runAndWait()

def say(text):
    try:
        google_tts(text)
        tts = "google"
    except:
        py_tts(text)
        tts = "py"
    # if tts == "google":
    #     time_to_say = (len(text.split())/170) * 60
    #     time.sleep(time_to_say)
    return {"text": text, "tts": tts}

def listen(timeout=10, phrase_time_limit=10, ready='', wake_word=False):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        if ready != '':
            say(ready)
        print('Listening: ')
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        try:
            text = recognizer.recognize_google(audio).lower()
            print(f"You said: {text}")
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
            text = 'Sorry, I didnt understand your request'
        except sr.RequestError as e:
            print(f"Could not request results from Speech Recognition service; {e}")
            text = 'Sorry, I didnt understand your request'
        if not wake_word and text != 'Sorry, I didnt understand your request':
            send_chat('user', text)
        return text

def listen_for_wake_word(ready=''):
    global wake_word
    input = listen(timeout=120, phrase_time_limit=5, ready=ready, wake_word=True)
    if wake_word in input:
        return True
    else:
        return False

def use_audio(audio):
    global is_audio
    is_audio = audio

def send_chat(sender, text):
    print(f'Sending chat to renderer: {text}')
    try:
        socket = get_app_socket()[1]
        if sender == 'assistant':
            socket.emit('response', {'purpose': 'chat-assistant', 'data': text})
        elif sender == 'user':
            socket.emit('response', {'purpose': 'chat-user', 'data': text}) 
    except Exception as e:
        print(e)