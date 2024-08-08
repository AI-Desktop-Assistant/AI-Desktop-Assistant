from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from config_socketio import get_app_socket
from reception_layer.speech_rec import say

load_dotenv(dotenv_path='.env')
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)

def process_generic_req(query):
    response = llm.invoke(query)
    say(response.content)
    return response