import os
from crewai import Agent, Task, Crew, Process, LLM,Flow
from crewai.flow.flow import listen, start
from dotenv import load_dotenv
from crewai_tools import PGSearchTool, PDFSearchTool
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.utilities import EmbeddingConfigurator
from typing import List
from pydantic import BaseModel, Field

load_dotenv()
os.environ['GEMINI_MODEL_NAME'] = 'gemini/gemini-1.5-flash'
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'

GEMINI_API_KEY=os.getenv('api_gemini')
# GOOGLE_API_KEY = os.getenv('api_google')
# Option 2. Vertex AI IAM credentials for Gemini, Anthropic, and anything in the Model Garden.
# https://cloud.google.com/vertex-ai/generative-ai/docs/overview

llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=GEMINI_API_KEY,
    temperature=0.7
)

tooldb = PGSearchTool(
    db_uri='postgresql://neondb_owner:6yCR0BKXOcrg@ep-morning-cloud-a55z1d5c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require',
    table_name='cursos'
)


tooldb_clases = PGSearchTool(
    db_uri='postgresql://neondb_owner:6yCR0BKXOcrg@ep-morning-cloud-a55z1d5c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require',
    table_name='lessons',
    search_query="SELECT title, description, duration, resource_key FROM lessons WHERE course_id IN (SELECT id FROM courses WHERE title ILIKE '%{curso}%');"
)

pdf_tool = PDFSearchTool()

# Agente para analizar las clases (lessons) dentro de un curso
# Agente encargado de buscar clases dentro de un curso específico
analista_de_clases = Agent(
    role="Asesor de Clases",
    goal="Buscar todas las clases del curso {curso}, extrayendo descripción y recursos.",
    backstory="Eres un experto en bases de datos con experiencia en la búsqueda académica.",
    tools=[tooldb_clases]
)

# Agente para analizar recursos PDF asociados a las clases
analista_de_recursos = Agent(
    role="Analista de Recursos",
    goal="Verificar si las clases del curso {curso} tienen PDFs en la columna 'resource_key' y extraer información.",
    backstory="Eres un especialista en análisis de contenido digital y extracción de información de documentos PDF.",
    tools=[tooldb_clases, pdf_tool]
)

# Agente para generar resúmenes y responder preguntas
resumen_clases = Agent(
    role="Redactor de clases",
    goal="Analizar la información extraída de las clases del curso {curso} y generar un resumen estructurado.",
    backstory="Eres un profesor experto en el curso {curso}, con habilidades en la síntesis de información.",
)

# Tarea para buscar clases dentro de un curso específico
task_clases = Task(
    description="""
    Buscar en la base de datos todas las clases del curso {curso}.
    Extraer descripción y recursos de cada clase.
    """,
    expected_output="Lista con detalles de las clases en el curso {curso}.",
    agents=[analista_de_clases],
)

# Tarea para revisar los recursos de las clases y extraer PDFs si existen
task_recursos = Task(
    description="""
    Revisar la columna 'resource_key' en la base de datos de lessons para identificar recursos PDF.
    Si hay archivos PDF, extraer el contenido y utilizarlo como fuente de información.
    """,
    expected_output="Lista de recursos encontrados y contenido extraído de PDFs.",
    agents=[analista_de_recursos],
)

# Tarea para resumir la información de las clases y responder preguntas
task_resumen_clases = Task(
    description="""
    Generar un resumen de la información de las clases del curso {curso} utilizando los datos extraídos.
    """,
    expected_output="Resumen detallado del contenido de las clases en el curso {curso}.",
    agents=[resumen_clases],
)


manager = Agent(
    role="Project Manager",
    goal="""
    Eres el lider del area de cursos y tutorias. tu objetivo es coordinar las tareas del equipo
    de manera eficiente, asegurando que solo se ejecuten las necesarias segun el input del usuario. 
    
    """,
    backstory="""
    Eres un experto en tutorias y cursos con experiencia en la extraccion de informacion relevante
    y en la redaccion de informes detallados. Tu objetivo es coordinar las tareas del equipo.
    """,
    allow_delegation=True,  # Permite asignar tareas automáticamente
    # verbose=True
    # llm=llm
)

crew_guia_cursos = Crew(
    agents=[
        analista_de_clases,
        resumen_clases        
        ],
    tasks=[
        task_clases,
        task_resumen_clases
        ],
    manager_agent=manager,
    process=Process.hierarchical,
    verbose=True,
    cache = True,
    language="spanish",
    
)
inputs = {
    "curso": "Big Data y Análisis de Datos",
    "pregunta": "que es big data?"
}
result = crew_guia_cursos.kickoff(inputs=inputs)
print(result)