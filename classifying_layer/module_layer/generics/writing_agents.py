from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.2)

def create_fact_agent():
    return Agent(
        role='Fact-Based Question Answering Agent',
        goal="""Your goal is to answer factual questions based on user input. You should provide concise, accurate information and avoid giving opinions or advice.""",
        backstory="""You are skilled at providing accurate and concise answers to factual questions.""",
        llm=llm,
        verbose=False
    )

def create_advice_agent():
    return Agent(
        role='Advice-Based Question Answering Agent',
        goal="""Your goal is to provide advice based on user input. Your advice should be practical, relevant, and considerate of the user's situation.""",
        backstory="""You are skilled at understanding user concerns and providing thoughtful and practical advice.""",
        llm=llm,
        verbose=False
    )

def create_definition_agent():
    return Agent(
        role='Definition-Based Question Answering Agent',
        goal="""Your goal is to provide definitions for terms or concepts based on user input. Your definitions should be clear, concise, and easy to understand.""",
        backstory="""You are skilled at providing clear and concise definitions for a wide range of terms and concepts.""",
        llm=llm,
        verbose=False
    )

def answer_fact_question(fact_agent, question):
    fact_task = Task(
        description=f"""Question: {question}
Provide a factual answer to the question. Ensure that your answer is concise and accurate.""",
        expected_output="Answer: (Concise and accurate factual answer)",
        agent=fact_agent
    )
    return fact_task.execute()

def answer_advice_question(advice_agent, question):
    advice_task = Task(
        description=f"""Question: {question}
Provide practical and relevant advice based on the question. Consider the user's situation and provide thoughtful guidance.""",
        expected_output="Advice: (Practical and relevant advice)",
        agent=advice_agent
    )
    return advice_task.execute()

def answer_definition_question(definition_agent, term):
    definition_task = Task(
        description=f"""Term: {term}
Provide a clear and concise definition for the term.""",
        expected_output="Definition: (Clear and concise definition)",
        agent=definition_agent
    )
    return definition_task.execute()

def generate_answer(question, question_type):
    if question_type == 'fact':
        fact_agent = create_fact_agent()
        answer = answer_fact_question(fact_agent, question)
    elif question_type == 'advice':
        advice_agent = create_advice_agent()
        answer = answer_advice_question(advice_agent, question)
    elif question_type == 'definition':
        definition_agent = create_definition_agent()
        answer = answer_definition_question(definition_agent, question)
    else:
        answer = "Invalid question type provided."
    
    return answer

# Example usage
if __name__ == "__main__":
    question = "What is the capital of France?"
    question_type = "fact"
    answer = generate_answer(question, question_type)
    print(answer)

    question = "How can I improve my time management skills?"
    question_type = "advice"
    answer = generate_answer(question, question_type)
    print(answer)

    term = "Quantum Computing"
    question_type = "definition"
    answer = generate_answer(term, question_type)
    print(answer)