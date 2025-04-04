import os
import getpass
from dotenv import load_dotenv
from crewai import LLM

from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = 'gemini'

if model == 'openai':
  os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'
  if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")
  chat = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
  llm = LLM(
      model="openai/gpt-4o-mini", # call model by provider/model_name
      temperature=0.1,    
      seed=42
  )
elif model == 'gemini':
  os.environ['GEMINI_MODEL_NAME'] = 'gemini/gemini-1.5-flash'
  if not os.environ.get("GEMINI_API_KEY"):
    os.environ["GEMINI_API_KEY"] = getpass.getpass("Enter API key for Gemini: ")
  chat = ChatGoogleGenerativeAI(
      model='gemini-1.5-flash',
      temperature=0.1,
      google_api_key=os.environ["GEMINI_API_KEY"]
  )
  llm = LLM(
      model=os.environ["GEMINI_MODEL_NAME"],
      temperature=0.1,
      seed=42
  )
aws = os.environ.get("AWS_URL")
DATABASE_URL = os.environ.get("BD_CONECTION")
DOWNLOAD_FOLDER = "downloads"
PDF_FOLDER = "pdf_resources"
