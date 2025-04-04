
from typing import List
from pydantic import BaseModel
from crewai import Agent, Task, Crew, Process
from tools.custom_tools import BDSearchTool
from crewai_tools import PDFSearchTool
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import llm
from tools.memory import MemoryManager


bd_search_tool = BDSearchTool()

#Definir salida de eventos
class EventOutput(BaseModel):
    events: List[str]

# Agente para analizar clases y extraer recursos
analista_de_clases = Agent(
    role="Analista de bases de datos",
    goal="Buscar todas las clases del curso {curso}, extrayendo la descripción y los recursos. Con base en la información, responder las preguntas {prompt}.",
    backstory="Eres un profesor experto en bases de datos con experiencia en tutorías en {curso}.",
    tools=[bd_search_tool],
    max_iter=3,
    llm=llm
)

task_clases = Task(
    description="""
    Buscar en la base de datos todas las clases del curso {curso}. Extraer descripción y los URLs de recursos.

    Luego, utilizando únicamente la información extraída de la base de datos,
    responde a la siguiente pregunta: {prompt}.

    Si la información extraída no contiene una respuesta clara, responde con:
    "No hay suficiente información en la base de datos para responder esta pregunta".
    """, 
    expected_output="Lista de descripciones de clases y URLs de recursos.",
    agent=analista_de_clases,
    output_pydantic=EventOutput  
)

#Agente para procesar PDFs
lector_pdf = Agent(
    role="Lector de PDF",
    goal="Leer y procesar los PDFs de los recursos extraídos para responder preguntas.",
    backstory="Eres un experto en la extracción de información de PDFs.",
    max_iter=3,
    llm=llm
)

#Herramienta PDF con URLs obtenidos de task_clases
pdf_tool = PDFSearchTool(file_paths=[]) 

# Tarea para procesar PDFs y responder preguntas
task_responder = Task(
    description="""
    Usando exclusivamente la información contenida en los PDFs extraídos,
    responde la siguiente pregunta: {prompt}.
    
    No uses información externa. Si la información obtenida no es suficiente,
    responde con "No hay suficiente información en la base de datos para responder esta pregunta".
    """,
    expected_output="Respuesta específica basada en los PDFs analizados.",
    agent=lector_pdf,
    context=[task_clases],  
    tools=[pdf_tool],  
)

# Agente Manager
manager = Agent(
    role="Manager",
    goal="Coordinar el flujo de información y responder preguntas basadas en la información extraída.",
    backstory="Eres un experto en gestión del conocimiento y síntesis de información.",
    max_iter=3,
    # memory = True,

)

# Crew con flujo de trabajo optimizado
crew_guia_cursos = Crew(
    agents=[analista_de_clases, lector_pdf],
    tasks=[task_clases, task_responder],
    process=Process.hierarchical,
    manager_agent=manager,  # Manager supervisa el proceso y entrega la respuesta final
    cache=True,
    llm=llm,
    # memory= True,
    # long_term_memory = LongTermMemory(
    #     storage=LTMSQLiteStorage(
    #         db_path="/my_crew1/long_term_memory_storage.db"
    #     )
    # ),
)




def classes_crew(user_id, data):
    agent_id = "classes"
    
    memory_manager = MemoryManager(user_id, agent_id)
    memory_manager.add_user_message(data.get("prompt", "")) 
      

    # Aquí estás usando otra función que devuelve un objeto tipo respuesta
    response = crew_guia_cursos.kickoff(inputs=data)

    if hasattr(response, "raw"):
        memory_manager.add_ai_message(response.raw)
        result = response.raw
    else:
        result = str(response)
        memory_manager.add_ai_message(result)

    memory_manager.save()

    return result