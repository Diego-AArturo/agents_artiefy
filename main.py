import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
from crewai_tools import YoutubeVideoSearchTool, PGSearchTool, PDFSearchTool
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from crewai.utilities import EmbeddingConfigurator
from typing import List
from pydantic import BaseModel, Field

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

# Option 1. Gemini accessed with an API key.
# https://ai.google.dev/gemini-api/docs/api-key
load_dotenv()
GEMINI_API_KEY=os.getenv('api_gemini')
GOOGLE_API_KEY = os.getenv('api_google')
# Option 2. Vertex AI IAM credentials for Gemini, Anthropic, and anything in the Model Garden.
# https://cloud.google.com/vertex-ai/generative-ai/docs/overview

llm = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=GEMINI_API_KEY,
    temperature=0.7
)

# youtube = YoutubeVideoSearchTool()

youtube = YoutubeVideoSearchTool(
    config=dict(
        
        llm=dict(
            
            provider="google", # or google, openai, anthropic, llama2, ...
            config=dict(
                model="gemini/gemini-1.5-flash",
                api_key=GEMINI_API_KEY,
                # temperature=0.5,
                # top_p=1,
                # stream=true,
            ),
        ),
        embedder=dict(
            provider="google", # or openai, ollama, ...
            config=dict(
                model="models/embedding-001",
                task_type="retrieval_document",
                # title="Embeddings",
            ),
        ),
    )
)

# tool = PGSearchTool(
#     db_uri='postgresql://neondb_owner:6yCR0BKXOcrg@ep-morning-cloud-a55z1d5c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require',
#     table_name='cursos'
# )

video_researcher = Agent(
    role="Content Researcher",
    goal="Analyze YouTube videos and extract key insights based on a given prompt.",
    backstory="You're an expert in video content analysis, specializing in extracting valuable information from YouTube videos related to technology and education. Your expertise ensures accurate and efficient retrieval of relevant insights.",
    allow_delegation=False,
    llm=llm,
    tools=[youtube]
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
    llm=llm,
    embedder_config=embedder,
    # api_key=GEMINI_API_KEY

)

planificador_proyecto = Agent(
    role="Planificador de Proyectos",
    goal="Desglosar meticulosamente el proyecto {project_type} en tareas accionables, asegurando que no se pase por alto ningún detalle y estableciendo cronogramas precisos alineados con los {project_objectives}.",
    backstory="Como un senior gestor de proyectos, has liderado numerosos proyectos exitosos en {industry}. Tu atención al detalle y pensamiento estratégico han garantizado siempre la entrega a tiempo y dentro del alcance. Ahora, tienes la tarea de planificar el próximo proyecto innovador {project_type}.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

analista_estimacion = Agent(
    role="Analista Experto en Estimaciones",
    goal="Proporcionar estimaciones altamente precisas de tiempo, recursos y esfuerzo para cada tarea del proyecto {project_type}, asegurando que se entregue de manera eficiente y dentro del presupuesto.",
    backstory="Eres el experto de referencia en estimación de proyectos en {industry}. Con una gran experiencia y acceso a datos históricos, puedes predecir con precisión los recursos necesarios para cualquier tarea, evitando retrasos innecesarios o sobrecostos.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

estratega_asignacion = Agent(
    role="Estratega de Asignación de Recursos",
    goal="Optimizar la asignación de tareas en el proyecto {project_type}, equilibrando las habilidades, disponibilidad y carga de trabajo del equipo para maximizar la eficiencia y el éxito del proyecto.",
    backstory="Con un profundo conocimiento de la dinámica de equipos y la gestión de recursos en {industry}, tienes un historial probado en la asignación eficiente de tareas, asegurando que cada miembro del equipo trabaje en la tarea más adecuada sin sobrecargarse.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# Definición de las tareas
tarea_desglose = Task(
    description="Analizar cuidadosamente los requisitos del proyecto {project_type} y desglosarlos en tareas individuales. Definir el alcance de cada tarea en detalle, establecer cronogramas alcanzables y asegurar que todas las dependencias sean consideradas: {project_requirements}. Miembros del equipo: {team_members}",
    expected_output="Una lista completa de tareas con descripciones detalladas, cronogramas, dependencias y entregables. La salida final DEBE incluir un diagrama de Gantt u otra visualización de la línea de tiempo específica para el proyecto {project_type}.",
    agents=[planificador_proyecto]
)

tarea_estimacion = Task(
    description="Evaluar minuciosamente cada tarea en el proyecto {project_type} para estimar el tiempo, recursos y esfuerzo requeridos. Utilizar datos históricos, complejidad de la tarea y recursos disponibles para proporcionar una estimación realista.",
    expected_output="Un informe detallado con la estimación de tiempo, recursos y esfuerzo requeridos para cada tarea en el proyecto {project_type}. El informe final DEBE incluir un resumen de cualquier riesgo o incertidumbre asociados con las estimaciones.",
    agents=[analista_estimacion]
)

tarea_asignacion = Task(
    description="Asignar estratégicamente las tareas del proyecto {project_type} a los miembros del equipo según sus habilidades, disponibilidad y carga de trabajo actual. Asegurar que cada tarea se asigne al miembro más adecuado y que la carga de trabajo esté distribuida equitativamente. Miembros del equipo: {team_members}",
    expected_output="Un diagrama de asignación de recursos mostrando qué miembros del equipo son responsables de cada tarea en el proyecto {project_type}, junto con fechas de inicio y finalización. La salida final DEBE incluir también un resumen explicando la lógica detrás de cada decisión de asignación.",
    agents=[estratega_asignacion],
    output_pydantic=ProjectPlan
)

# Define your task
task_video = Task(
    description="Generate a text document in spanish based on the insights extracted from the YouTube videos with the timestamps of where to extract the information.",
    expected_output="A text document in spanish with the insights extracted from the YouTube videos",
    agents=[video_researcher],
)
task_rag_general = Task(
    description="Responde a las preguntas del usuario sobre la institucion CIADET ylos programas que ofrecen con la informacion proporcionada en el contexto",
    expected_output="una respuesta a la pregunta del usuario",
    agents=[rag_general],
)
# Define the manager agent
manager = Agent(
    role="Project Manager",
    goal="Debes coordinar las tareas del equipo, asegurandote de asignar las tareas correctamente y asegurarte de que se completen a tiempo y con la mayor calidad posible.",
    backstory="Eres Artiefy, el gerente de proyecto de la tripulación. Tu objetivo es coordinar las tareas del equipo, asegurándote de asignar las tareas correctamente y de que se completen a tiempo y con la mayor calidad posible. Tu experiencia en la gestión de proyectos y la coordinación de equipos te permite liderar eficazmente a tu tripulación hacia el éxito.",
    allow_delegation=True,
    llm=llm
)

# Instantiate your crew with a custom manager
crew = Crew(
    agents=[
        # video_researcher,
        rag_general,
        planificador_proyecto,
        analista_estimacion,
        estratega_asignacion
        ],
    tasks=[
        # task_video,
        task_rag_general,
        tarea_desglose, 
        tarea_estimacion,
        tarea_asignacion
        ],
    manager_agent=manager,
    process=Process.hierarchical,
    verbose=True,
    language="es",
    
)

project = 'Website'
industry = 'Technology'
project_objectives = 'Create a website for a small business'
team_members = """
- John Doe (Project Manager)
- Jane Doe (Software Engineer)
- Bob Smith (Designer)
- Alice Johnson (QA Engineer)
- Tom Brown (QA Engineer)
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
inputs = {
    'project_type': project,
    'project_requirements': project_requirements,
    'project_objectives': project_objectives,
    'team_members': team_members,
    'industry': industry
}
# Start the crew's work
result = crew.kickoff(inputs=inputs)
print(result)