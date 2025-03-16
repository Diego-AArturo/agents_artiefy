import os
import getpass
from dotenv import load_dotenv
from crewai import LLM
# os.environ['GEMINI_MODEL_NAME'] = 'gemini/gemini-1.5-flash'
from langchain_openai import ChatOpenAI

load_dotenv()
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'
if not os.environ.get("OPENAI_API_KEY"):
  os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for OpenAI: ")

chat = ChatOpenAI(model="gpt-4", temperature=0.2)
llm = LLM(
    model="openai/gpt-4", # call model by provider/model_name
    temperature=0.2,    
    seed=42
)
aws = os.environ.get("AWS_URL")
DATABASE_URL = os.environ.get("BD_CONECTION")
DOWNLOAD_FOLDER = "downloads"
PDF_FOLDER = "pdf_resources"