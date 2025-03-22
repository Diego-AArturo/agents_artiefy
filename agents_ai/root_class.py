
from crewai import Agent, Task, Crew, Process
from tools.custom_tools import CourseRootTool
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import llm


# bd_search_tool = bd_search_root


buscador_de_cursos = Agent(
    role="Buscador de cursos",
    goal="Identificar los cursos de Artiefy que se alineen con la necesidad {prompt}.",
    backstory="Eres un experto en asesoria educativa y busqueda de cursos. Puedes encontrar cursos relevantes para cualquier necesidad.",
    tools=[CourseRootTool()],
    # verbose=True,
    max_iter=3,
    llm=llm
)

# 🔹 Agente: Analista de cursos (Evalúa relevancia)
analista_de_cursos = Agent(
    role="Analista de cursos",
    goal="Evaluar y clasificar los cursos encontrados en la base de datos con respecto a su relevancia con la necesidad {prompt}.",
    backstory="Eres un especialista en análisis de contenido y recomendación educativa. Puedes evaluar cursos y determinar su aplicabilidad.",
    #verbose=True,
    max_iter=3,
    llm=llm
)

# 🔹 Tarea 1: Buscar cursos relevantes en la base de datos
task_buscar_cursos = Task(
    description="Buscar cursos en la base de datos de Artiefy que coincidan con la necesidad del usuario.",
    expected_output="Una lista con los titulos y descripciones de los cursos mas relevantes.",
    agent=buscador_de_cursos,
)

# 🔹 Tarea 2: Analizar y clasificar los cursos encontrados
task_analizar_cursos = Task(
    description="Analizar y clasificar los cursos según su descripcion y relevancia para el usuario. Solo devolver los 5 cursos más relevantes.Estos cursos deben estar en la base de datos",
    expected_output="Lista solo con los titulos o nombres de los 5 cursos más relevantes.",
    agent=analista_de_cursos,
)


# 🔹 Crew que ejecuta el proceso completo
crew_class = Crew(
    agents=[buscador_de_cursos, analista_de_cursos],
    tasks=[task_buscar_cursos, task_analizar_cursos],
    # manager_agent=manager,
    process=Process.sequential,  # 🛠 Ejecuta en orden
    # verbose=True,
    language="spanish",
)

# inputs = {
#     "prompt": "desarrollo de videojuegos."
# }

# result = crew_class.kickoff(inputs=inputs)
# print(result)