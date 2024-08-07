import speech_recognition as sr
import pyttsx3
from google.cloud import texttospeech
from config_socketio import get_app_socket
import pygame
import io
import os
import threading

wake_word = 'hey computer'
assistant_volume = 0.5
assistant_voice = 'B'
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gcp_creds\\ai-desktop-assistant-425120-fc21e54bf79d.json'
client = texttospeech.TextToSpeechClient()
pygame.mixer.init(frequency=24000)
tts_engine.setProperty('volume', 0.5)
pygame.mixer.music.set_volume(0.1)

is_audio = True
received_message = None
received_text = None
input_event = threading.Event()
stop_event = threading.Event()

def change_volume(volume):
    conv_volume = int(volume) / 1000
    print(f'Setting Volume: {conv_volume}')
    pygame.mixer.music.set_volume(conv_volume)
    

def change_voice(voice):
    global assistant_voice
    print(f'Setting Voice to: {voice}')
    assistant_voice = voice[-1]

def google_tts(text):
    print(f'Returning chat: {text}')
    send_chat('assistant', text)
    if is_audio:
        global assistant_voice
        print("playing google")
        input_text = texttospeech.SynthesisInput(text=text)
        print('Synthesizing input')
        # selected_voice = get_selected_voice()
        print('Selecting Voice')
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name=f"en-US-Wavenet-{assistant_voice}",
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

def set_recieved_message(message):
    global received_message
    received_message = message
    print(f'Set Received message: {message}')

def say(text):
    print(f'Is Audio: {is_audio}')
    try:
        google_tts(text)
        tts = "google"
    except:
        py_tts(text)
        tts = "py"
    return {"text": text, "tts": tts}

def wait_for_message_from_ui():
    global received_message
    received_message = None
    socket = get_app_socket()[1]
    print('Waiting for message from UI')
    seconds = 0
    while not input_event.is_set() and not stop_event.is_set():
        socket.sleep(0.1)
        seconds += 0.1
    print(f'Received message From UI: {received_message}')

def listen_from_microphone(timeout, phrase_time_limit, ready):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        if ready != '':
            say(ready)
        try:
            print('Listening: ')
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            global received_text
            if not input_event.is_set() and not stop_event.is_set():
                text = recognizer.recognize_google(audio).lower()
                received_text = text
                input_event.set()
                print(f"You said: {text}")
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
            if not input_event.is_set() and not stop_event.is_set():
                received_text = 'Sorry, I didn\'t understand your request'
                input_event.set()
        except sr.RequestError as e:
            print(f"Could not request results from Speech Recognition service; {e}")
            if not input_event.is_set() and not stop_event.is_set():
                received_text = 'Sorry, I didn\'t understand your request'
                input_event.set()
        except Exception as e:
            print(e)
            if not input_event.is_set() and not stop_event.is_set():
                received_text = 'Sorry, I didn\'t understand your request'
                input_event.set()

def listen(timeout=10, phrase_time_limit=10, ready='', wake_word=False):
    try:
        global received_text
        global received_message
        print(f'Previous Recieved Message: {received_text}')
        print(f'Previous Recieved Message: {received_message}')

        received_message = None
        received_text = None
        print(f'Received Message Set to None: {received_message}')
        print(f'Received Text Set to None: {received_text}')

        input_event.clear()
        stop_event.clear()
        
        ui_thread = threading.Thread(target=wait_for_message_from_ui)
        mic_thread = threading.Thread(target=listen_from_microphone, args=(timeout, phrase_time_limit, ready))

        print('Starting UI Thread')
        ui_thread.start()
        print('Starting Mic thread')
        mic_thread.start()

        print('Waiting on input_event')
        input_event.wait()

        print('Setting Stop Event')
        stop_event.set()

        print('Terminating threads')
        ui_thread.join()
        print('Terminated UI thread')
        mic_thread.join()
        print('Terminated mic thread')

        print(f'Received Message: {received_message}')
        print(f'Received text: {received_text}')

        if received_message:
            print('Setting Use Audio: False')
            use_audio(False)
            print(f'Returning Message From UI: {received_message}')
            return received_message
        else:
            print(f'Returning message from Microphone: {received_text}')
            if received_text and received_text != 'Sorry, I didn\'t understand your request' and received_text != '':
                if wake_word:
                    if 'hey computer' in received_text:
                        print('Setting Use Audio: True')
                        use_audio(True)
                        socket = get_app_socket()[1]
                        socket.emit('response', {'purpose': 'chat-user', 'data': received_text})
                else:
                    print('Setting Use Audio: True')
                    use_audio(True)
                    socket = get_app_socket()[1]
                    socket.emit('response', {'purpose': 'chat-user', 'data': received_text})
            return received_text
            
    except Exception as e:
        print(e)

def listen_for_wake_word(ready=''):
    try:
        print(f'Listening for wake workd')
        global wake_word
        input = listen(timeout=10, phrase_time_limit=5, ready=ready, wake_word=True)
        print(f'Output from listen: {input}')
        if wake_word in input or received_message:
            print(f'Wake Word Detected or UI')
            if received_message:
                print(f'Message from ui detected, returning recieved message')
                return received_message
            print('Wake Word Detected')
            return True
        else:
            return False
    except Exception as e:
        print(e)

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

if __name__ == '__main__':
    tts_engine.setProperty('volume', 0.5)