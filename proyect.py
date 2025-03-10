import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
import pandas as pd
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

class TaskBreakdown(BaseModel):
    task_name: str = Field(..., description="Nombre de la tarea")
    description: str = Field(..., description="Descripción detallada de la tarea")
    dependencies: List[str] = Field(..., description="Lista de tareas de las que depende esta tarea")
    estimated_duration_hours: float = Field(..., description="Duración estimada en horas")


load_dotenv()
#os.environ['GEMINI_MODEL_NAME'] = 'gemini/gemini-1.5-flash'
os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')
os.environ['OPENAI_MODEL_NAME'] = 'gpt-4o-mini'
#GEMINI_API_KEY=os.getenv('api_gemini')

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
    
    Miembros del equipo:
    {team_members}""",
    expected_output="""
    Un diagrama de asignación de recursos mostrando qué miembros del equipo son responsables de cada tarea
    en el proyecto {project_type}, junto con fechas de inicio y finalización. Tu output final DEBE incluir
    un resumen explicando la justificación detrás de cada decisión de asignación.""",
    agents=[estratega_asignacion],
    output_pydantic=ProjectPlan  # ⬅ Definir salida estructurada
)
manager = Agent(
    role="Project Manager",
    goal="""
    Eres el gerente de operaciones de la tripulación. Tu objetivo es coordinar las tareas del equipo 
    de manera eficiente, asegurando que solo se ejecuten las necesarias según el input del usuario. 
    
    """,
    backstory="""
    Eres un experto en gestión de proyectos y automatización de procesos. 
    Con años de experiencia en inteligencia artificial y organización, 
    puedes analizar rápidamente la información del usuario y estructurar un plan de ejecución eficiente. 
    Tu enfoque es claro, preciso y siempre busca maximizar la productividad de la tripulación.
    """,
    allow_delegation=True,  # Permite asignar tareas automáticamente
    verbose=True
    # llm=llm
)

crew = Crew(
    agents=[        
        planificador_proyecto,
        analista_estimacion,
        estratega_asignacion
        ],
    tasks=[       
        tarea_desglose, 
        tarea_estimacion,
        tarea_asignacion
        ],
    manager_agent=manager,
    verbose=True,
    cache = True,
    language="Spanish",
    process=Process.hierarchical
)



project = 'Website'
industry = 'Technology'
project_objectives = 'Create a website for a small business'
team_members = """
- Diego Arturo (Project Manager, Web Developer)

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
print(result.pydantic.dict())

tasks = result.pydantic.dict()['tasks']
df_tasks = pd.DataFrame(tasks)

# Display the DataFrame as an HTML table
df_tasks.style.set_table_attributes('border="1"').set_caption("Task Details").set_table_styles(
    [{'selector': 'th, td', 'props': [('font-size', '120%')]}]
)

milestones = result.pydantic.dict()['milestones']
df_milestones = pd.DataFrame(milestones)

# Display the DataFrame as an HTML table
df_milestones.style.set_table_attributes('border="1"').set_caption("Task Details").set_table_styles(
    [{'selector': 'th, td', 'props': [('font-size', '120%')]}]
)