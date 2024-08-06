from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='.env')
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model_name="gpt-3.5-turbo-0125", temperature=0.2)

def create_subject_gen_agent():
    return Agent(
        role='Email Subject Generation Agent',
        goal="""Your goal is to generate formal email subjects(NOT EMAIL BODY) using user input requests. You do not generate email bodies, footers, signatures, or any other email text, other than email subjects. When creating an email subject, ensure that the subject is concise and only pertains to the intent of the email. Your generated subject should not include information about email recipients, cc recipients, or bcc recipients, UNLESS ABSOLUTELY NECESSARY for the subject of the email to sufficiently describe what the email is about.""",
        backstory="""You are skilled at understanding the meaning and intent in user inputs. You are especially skilled in crafting professional and formal email subjects from user inputs.""",
        llm=llm,
        verbose=False
    )

def create_body_gen_agent():
    return Agent(
        role='Email Body Generation Agent',
        goal="""Your goal is to generate formal email bodies(NOT SUBJECTS, NOT FOOTERS). You do not generate email subjects, footers, signatures, or any other email text other than email bodies.""",
        backstory="""You are skilled at crafting professional and formal email bodies from user requests.""",
        llm=llm,
        verbose=False
    )

def create_signature_remover_agent():
    return Agent(
        role="Email Signature Remover Agent",
        goal="Your goal is to remove email signatures from emails and return the same email without an email signature. An email signature is the end of the email where you'll see 'Best Regards,' or 'Sincerely,' followed by a name. You remove these email signatures leaving only the email greeting at the begining of the email, and the email body.",
        backstory="""You are skilled at understanding the different parts of an email(the greeting, the body, and the signature). You are especially skilled at recognizing where the signature is in an email and at removing the signature of an email only leaving the email greeting and the email body.""",
        llm=llm,
        verbose=False
    )

def gen_clean_body(signature_remover_agent, body):
    signature_remover_task = Task(
        description=f"""Email: {body}
Analyze the email and find if there is an email signature at the end of the email. If you see an email signature at the end of the email, remove the email signature from the email and output only the email greeting and email body with no email signature. Some common email signatures are:
Best Regards,
[your name]
or
Sincerely,

The email signature may or may not contain '[Your Name]' following 'Best Regards,', 'Sincerely,', or any other email signature. Either way, whether or not '[Your Name]' is present, the email signature must be removed.
If you do not find an email signature then you will return the email in its original state.

IF you find an email signature THEN appropriately output the email with no signature.
ELSE IF you do not find an email THEN appropriately output the original email.
""",
        expected_output="""Body: (Original email body without an email signature)""",
        agent=signature_remover_agent
    )
    return signature_remover_task.execute()

def gen_body(body_gen_agent, req, context):
    body_task = Task(
        description=f"""User Input: {req}
Context: {str(context)}
Generate a formal email body with no footer, subject, email signature or closing signature, using the provided user input and context if available. DO NOT add a "Sincerely," or "Best Regards," signature/closer to the end of the email, only generate the greeting and main body of content with no signature or closing regards.
An example of an acceptable format for the body you will generate is as follows:
Dear [names of recipients],

I hope this email finds you well. I am writing to provide you with a follow-up on the progress of the project NBC. We have made significant strides in the development phase and are on track to meet the agreed-upon deadlines. 

If you have any questions or require further information, please do not hesitate to reach out. Your feedback and input are highly valued as we work towards successfully completing the project.

Thank you for your continued partnership and support.

An example of an UNACCEPTABLE formate for the body you will generate is as follows:
Dear [names of recipients],

I hope this email finds you well. I am writing to provide you with a follow-up on the progress of the project NBC. We have made significant strides in the development phase and are on track to meet the agreed-upon deadlines. 

If you have any questions or require further information, please do not hesitate to reach out. Your feedback and input are highly valued as we work towards successfully completing the project.

Thank you for your continued partnership and support.

Best Regards,
[Your Name]

Notice that the UNACCEPTABLE generated body contains an email signature at the end of the email that says:
Best Regards,
[Your Name]
This entire portion of the emailand anything similar is prohibited from being in your generated in your outputted email.
""",
        expected_output="""
Body: (Generated email body with no subject, footer, or signature)""",
        agent=body_gen_agent
    )
    return body_task.execute()

def gen_subject(subject_gen_agent, req, context):
    subject_task = Task(
        description=f"""Generate a formal email subject with no footer, subject, or signature using the provided user input and context if available.
        User Input: {req}
        Context: {str(context)}""",
        expected_output="""
Subject: (Generated email subject with no subject, footer, or signature)""",
        agent=subject_gen_agent
    )
    return subject_task.execute()

def clean_body_and_sub(body, subject):
    split_body = body.split(':')
    split_subject = subject.split(':')
    clean_body = ''
    clean_subject = ''
    for idx, val in enumerate(split_body):
        if idx != 0:
            if idx != len(split_body) - 1:
                clean_body += val
                clean_body += ':'
            else:
                clean_body += val
    
    for idx, val in enumerate(split_subject):
        if idx != 0:
            if idx != len(split_subject) - 1:
                clean_subject += val
                clean_subject += ':'
            else:
                clean_subject += val
    return clean_body.strip(), clean_subject.strip()

def gen_body_and_subject(body_gen_agent, subject_gen_agent, signature_remover_agent, req, context):
    body = gen_body(body_gen_agent, req, context)
    print(f'Body: {body}')
    cleaned_body = gen_clean_body(signature_remover_agent, body)
    print(f'Cleaned Body: {cleaned_body}')
    subject = gen_subject(subject_gen_agent, req, context)
    print(f'Subject: {subject}: {type(cleaned_body)}, {type(subject)}')
    return cleaned_body, subject

def generate_email(req, context):
    subject_gen_agent = create_subject_gen_agent()
    body_gen_agent = create_body_gen_agent()
    print('Created Writing Agents')
    signature_remover_agent = create_signature_remover_agent()
    body, subject = gen_body_and_subject(body_gen_agent, subject_gen_agent, signature_remover_agent, req, context)
    print(f'Generating Body and Subject: {type(body)}, {type(subject)}')
    clean_body, clean_subject = clean_body_and_sub(body, subject)
    print('Cleaned Body and subject')
    if len(clean_body) == 0 or len(clean_subject) == 0:
        if len(clean_body) == 0:
            print('Body not found')
        if len(subject) == 0:
            print('Subject not found')
        print('Regenerating Email')
        clean_body, clean_subject = generate_email(req, context)
    print('Returning Body and Subject')
    return clean_body, clean_subject