import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
from crewai_tools import PGSearchTool
from crewai.utilities import EmbeddingConfigurator
from typing import List
from pydantic import BaseModel, Field
from IPython.display import display, Markdown

# Cargar variables de entorno
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'

# Herramienta de búsqueda en la base de datos
tooldb = PGSearchTool(
    db_uri='postgresql://neondb_owner:6yCR0BKXOcrg@ep-morning-cloud-a55z1d5c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require',
    table_name='cursos'
)

buscador_de_cursos = Agent(
    role="Buscador de cursos",
    goal="Identificar cursos de Artiefy que se alineen con la necesidad del usuario.",
    backstory="Eres un experto en bases de datos con experiencia en búsqueda y extracción de información relevante sobre cursos.",
    tools=[tooldb],
    verbose=True
)

# 🔹 Agente: Analista de cursos (Evalúa relevancia)
analista_de_cursos = Agent(
    role="Analista de cursos",
    goal="Evaluar y clasificar los cursos encontrados en base a su relevancia con la necesidad del usuario.",
    backstory="Eres un especialista en análisis de contenido y recomendación educativa. Puedes evaluar cursos y determinar su aplicabilidad.",
    # verbose=True
)

# 🔹 Tarea 1: Buscar cursos relevantes en la base de datos
task_buscar_cursos = Task(
    description="Buscar cursos en la base de datos de Artiefy que coincidan con la necesidad del usuario.",
    expected_output="Lista de cursos relevantes con títulos.",
    agents=[buscador_de_cursos],
)

# 🔹 Tarea 2: Analizar y clasificar los cursos encontrados
task_analizar_cursos = Task(
    description="Analizar y clasificar los cursos según su relevancia para el usuario.",
    expected_output="Lista de solo los titulos de los cursos ordenados por nivel de coincidencia con la necesidad del usuario.",
    agents=[analista_de_cursos],
)

# 🔹 Project Manager (Coordina el flujo de trabajo)
manager = Agent(
    role="Project Manager",
    goal="Coordinar la búsqueda y análisis de cursos de manera eficiente.",
    backstory="Eres un experto en gestión de proyectos y automatización de procesos. Organizas tareas para optimizar resultados.",
    allow_delegation=True,
    # verbose=True
)

# 🔹 Crew que ejecuta el proceso completo
crew_class = Crew(
    agents=[buscador_de_cursos, analista_de_cursos],
    tasks=[task_buscar_cursos, task_analizar_cursos],
    manager_agent=manager,
    process=Process.hierarchical,  # 🛠 Ejecuta en orden
    # verbose=True,
    language="spanish",
)

# inputs = {
#     "prompt": "Quiero aprender sobre desarrollo de video juegos."
# }

# result = crew_class.kickoff(inputs=inputs)
# print(result)