import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
from crewai_tools import YoutubeVideoSearchTool, PGSearchTool, PDFSearchTool
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.utilities import EmbeddingConfigurator
from typing import List
from pydantic import BaseModel, Field
from IPython.display import display, Markdown




class TaskEstimate(BaseModel):
    task_name: str = Field(..., description="Name of the task")
    estimated_time_hours: float = Field(..., description="Estimated time to complete the task in hours")
    required_resources: List[str] = Field(..., description="List of resources required to complete the task")

class Milestone(BaseModel):
    milestone_name: str = Field(..., description="Name of the milestone")
    tasks: List[str] = Field(..., description="List of task IDs associated with this milestone")

class ProjectPlan(BaseModel):
    tasks: List[TaskEstimate] = Field(..., description="List of tasks with their estimates")
    milestones: List[Milestone] = Field(..., description="List of project milestones")

class TaskBreakdown(BaseModel):
    task_name: str = Field(..., description="Nombre de la tarea")
    description: str = Field(..., description="Descripción detallada de la tarea")
    dependencies: List[str] = Field(..., description="Lista de tareas de las que depende esta tarea")
    estimated_duration_hours: float = Field(..., description="Duración estimada en horas")


# Option 1. Gemini accessed with an API key.
# https://ai.google.dev/gemini-api/docs/api-key
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

# youtube = YoutubeVideoSearchTool()



tooldb = PGSearchTool(
    db_uri='postgresql://neondb_owner:6yCR0BKXOcrg@ep-morning-cloud-a55z1d5c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require',
    table_name='cursos'
)

analista_de_basedatos = Agent(
    role="Asesor de cursos",
    goal="Encontrar segun la descripcion de los curso ofrecidos por el CIADET cuales cubren mejor la necesidad del usuario ",
    backstory="Eres un experto en bases de datos con experiencia en la búsqueda y extracción de información relevante. Tu objetivo es encontrar información detallada sobre los cursos ofrecidos por el CIADET para asesorar al usuario que cursos le pueden servir para su objetivo.",
    tools=[tooldb],
)



pdf_source = PDFKnowledgeSource(
    chunk_size=5000,
    file_paths=["BOT_CIADET_EDITADO_HERMES.pdf"],
    
)
embedder={
        "provider": "google",
        "config": {
            "model": "models/text-embedding-004",
            "api_key": GEMINI_API_KEY,
        }
    }

# EmbeddingConfigurator().configure_embedder(embedder)
rag_general = Agent ( 
    role="Asesor general",
    goal="contestar preguntas basadas en la informacion proporcionada en el contexto",
    backstory="eres un asesor general que ayuda a los usuarios a encontrar información relevante y a responder preguntas basadas en la información proporcionada en el contexto. Tu objetivo es proporcionar respuestas precisas y útiles a las preguntas de los usuarios, utilizando la información disponible en el contexto.",
    allow_delegation=False,
    knowledge_sources=[pdf_source],
    # llm=llm,
    embedder_config=embedder,
    # api_key=GEMINI_API_KEY

)

planificador_proyecto = Agent(
    role="Planificador de Proyectos",
    goal="Desglosar meticulosamente el proyecto {project_type} en tareas accionables, asegurando que no se pase por alto ningún detalle y estableciendo cronogramas precisos alineados con los {project_objectives}.",
    backstory="Como un senior gestor de proyectos, has liderado numerosos proyectos exitosos en {industry}. Tu atención al detalle y pensamiento estratégico han garantizado siempre la entrega a tiempo y dentro del alcance. Ahora, tienes la tarea de planificar el próximo proyecto innovador {project_type}.",
    allow_delegation=False,
    verbose=True,
    # llm=llm
)

analista_estimacion = Agent(
    role="Analista Experto en Estimaciones",
    goal="Proporcionar estimaciones altamente precisas de tiempo, recursos y esfuerzo para cada tarea del proyecto {project_type}, asegurando que se entregue de manera eficiente y dentro del presupuesto.",
    backstory="Eres el experto de referencia en estimación de proyectos en {industry}. Con una gran experiencia y acceso a datos históricos, puedes predecir con precisión los recursos necesarios para cualquier tarea, evitando retrasos innecesarios o sobrecostos.",
    allow_delegation=False,
    verbose=True,
    # llm=llm
)

estratega_asignacion = Agent(
    role="Estratega de Asignación de Recursos",
    goal="Optimizar la asignación de tareas en el proyecto {project_type}, equilibrando las habilidades, disponibilidad y carga de trabajo del equipo para maximizar la eficiencia y el éxito del proyecto.",
    backstory="Con un profundo conocimiento de la dinámica de equipos y la gestión de recursos en {industry}, tienes un historial probado en la asignación eficiente de tareas, asegurando que cada miembro del equipo trabaje en la tarea más adecuada sin sobrecargarse.",
    allow_delegation=False,
    verbose=True,
    # llm=llm
)

# Definición de las tareas
tarea_desglose = Task(
    description="""
    Analizar cuidadosamente los requisitos del proyecto {project_type}
    y desglosarlos en tareas individuales. Definir el alcance de cada tarea en detalle,
    establecer cronogramas alcanzables y asegurar que todas las dependencias sean consideradas para:
    
    {project_requirements}
    
    Miembros del equipo:
    {team_members}
    """,
    expected_output="""
    Una lista completa de tareas con descripciones detalladas, cronogramas,
    dependencias y entregables. Tu output final DEBE incluir un Gráfico Gantt
    o visualización de línea de tiempo similar específica para el {Project_type} Proyecto.""",
    agents=[planificador_proyecto],
    output_pydantic=TaskBreakdown  # ⬅ Definir salida estructurada
)

tarea_estimacion = Task(
    description="""
    Evaluar cada tarea en el proyecto {project_type} para estimar el tiempo,
    recursos y esfuerzo requeridos.
    Utilizar datos históricos, complejidad de la tarea y recursos disponibles para
    proporcionar una estimación realista para cada tarea.""",
    expected_output="""
    Un informe detallado con la estimación de tiempo, recursos y esfuerzo requeridos
    para cada tarea in el proyecto {project_type}.
    Tu reporte final DEBE incluir un resumen de cualquier riesgo o incertidumbre
    asociado con la estimacion.""",
    agents=[analista_estimacion],
    output_pydantic=TaskEstimate  # ⬅ Definir salida estructurada
)

tarea_asignacion = Task(
    description="""
    Asignar estratégicamente las tareas del proyecto {project_type} a los miembros 
    del equipo según sus habilidades, disponibilidad y carga de trabajo actual. 
    Asegurate de que cada tarea esté claramente asignada a el miembro del equipo mas adecuado
    y que la carga de trabajo se distribuye uniformemente.
    En caso de solo tener un miembro en el equipo, asignarle todas las tareas. 
    
    Miembros del equipo:
    {team_members}""",
    expected_output="""
    Un diagrama de asignación de recursos mostrando qué miembros del equipo son responsables de cada tarea
    en el proyecto {project_type}, junto con fechas de inicio y finalización. Tu output final DEBE incluir
    un resumen explicando la justificación detrás de cada decisión de asignación.""",
    agents=[estratega_asignacion],
    output_pydantic=ProjectPlan  # ⬅ Definir salida estructurada
)

task_cursos = Task(
    description="Encontrar los cursos que se ofrece en Atriefy que cubren mejor la necesidad del usuario",
    expected_output="una lista de cursos que cubren mejor la necesidad del usuario",
    agents=[analista_de_basedatos],

)
# Define your task
# task_video = Task(
#     description="Generate a text document in spanish based on the insights extracted from the YouTube videos with the timestamps of where to extract the information.",
#     expected_output="A text document in spanish with the insights extracted from the YouTube videos",
#     agents=[video_researcher],
# )
task_rag_general = Task(
    description="Responde a las preguntas del usuario sobre la institucion CIADET ylos programas que ofrecen con la informacion proporcionada en el contexto",
    expected_output="una respuesta a la pregunta del usuario",
    agents=[rag_general],
)
# Define the manager agent
manager = Agent(
    role="Project Manager",
    goal="""
    Eres el gerente de operaciones de la tripulación. Tu objetivo es coordinar las tareas del equipo 
    de manera eficiente, asegurando que solo se ejecuten las necesarias según el input del usuario.
    """,
    backstory="""
    Eres un experto en gestión de proyectos y automatización de procesos. 
    puedes analizar rápidamente la información del usuario y estructurar un plan de ejecución eficiente. 
    Tu enfoque es claro, preciso y siempre busca maximizar la productividad de la tripulación.
    """,
    allow_delegation=True,  # Permite asignar tareas automáticamente
    verbose=True
    # llm=llm
)

# Instantiate your crew with a custom manager

crew = Crew(
    agents=[
        # video_researcher,
        # rag_general,
        # analista_de_basedatos,
        planificador_proyecto,
        analista_estimacion,
        estratega_asignacion
        ],
    tasks=[
        # task_video,
        # task_rag_general,
        # task_cursos,
        tarea_desglose, 
        tarea_estimacion,
        tarea_asignacion
        ],
    manager_agent=manager,
    process=Process.hierarchical,
    verbose=True,
    #cache = True,
    language="Spanish",
    
)

project = 'Website'
industry = 'Technology'
project_objectives = 'Create a website for a small business'
team_members = """
- Diego Arturo

"""
project_requirements = """
- Create a responsive design that works well on desktop and mobile devices
- Implement a modern, visually appealing user interface with a clean look
- Develop a user-friendly navigation system with intuitive menu structure
- Include an "About Us" page highlighting the company's history and values
- Design a "Services" page showcasing the business's offerings with descriptions
- Create a "Contact Us" page with a form and integrated map for communication
- Implement a blog section for sharing industry news and company updates
- Ensure fast loading times and optimize for search engines (SEO)
- Integrate social media links and sharing capabilities
- Include a testimonials section to showcase customer feedback and build trust
"""


# Format the dictionary as Markdown for a better display in Jupyter Lab
formatted_output = f"""
**Project Type:** {project}

**Project Objectives:** {project_objectives}

**Industry:** {industry}

**Team Members:**
{team_members}
**Project Requirements:**
{project_requirements}
"""
# Display the formatted output as Markdown
display(Markdown(formatted_output))

inputs = {
    'project_type': project,
    'project_requirements': project_requirements,
    'project_objectives': project_objectives,
    'team_members': team_members,
    'industry': industry
}
# inputs = {'prompt':'Quiero crear un videojuego de aventuras, ¿qué cursos me recomiendan?',
#         'project_type': 'None',
#         'project_requirements': 'None',
#         'project_objectives': 'None',
#         'team_members': 'None',
#         'industry': 'None'
# }
# Start the crew's work
result = crew.kickoff(inputs=inputs)
print(result)

h= result.pydantic.dict()
print(h)