import os
from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv
from crewai_tools import YoutubeVideoSearchTool, PGSearchTool, PDFSearchTool

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

tool = PGSearchTool(
    db_uri='postgresql://neondb_owner:6yCR0BKXOcrg@ep-morning-cloud-a55z1d5c-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require',
    table_name='cursos'
)

project_manager = Agent(
    role="Content Researcher",
    goal="Analyze YouTube videos and extract key insights based on a given prompt.",
    backstory="You're an expert in video content analysis, specializing in extracting valuable information from YouTube videos related to technology and education. Your expertise ensures accurate and efficient retrieval of relevant insights.",
    allow_delegation=False,
    llm=llm,
    tools=[youtube]
)

rag_general = Agent ( 
    role="RAG",
    goal="Answer questions based on the information provided in the context.",
    backstory="You're Artie an expert in answering questions based on the information provided in the context. Your expertise ensures accurate and efficient retrieval of relevant answers.",
    allow_delegation=False,
    llm=llm,
)

rag_profesor_subjet = Agent (

)
# Define your agents
Content_researcher = Agent(
    role="Content Researcher",
    goal="Analyze YouTube videos and extract key insights based on a given prompt.",
    backstory="You're an expert in video content analysis, specializing in extracting valuable information from YouTube videos related to technology and education. Your expertise ensures accurate and efficient retrieval of relevant insights.",
    allow_delegation=False,
    llm=llm,
    tools=[youtube]
)


# Define your task
task = Task(
    description="Generate a text document in spanish based on the insights extracted from the YouTube videos with the timestamps of where to extract the information.",
    expected_output="A text document in spanish with the insights extracted from the YouTube videos",
    agents=[Content_researcher],
)

# Define the manager agent
manager = Agent(
    role="Project Manager",
    goal="Efficiently manage the crew and ensure high-quality task completion",
    backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
    allow_delegation=True,
    llm=llm
)

# Instantiate your crew with a custom manager
crew = Crew(
    agents=[Content_researcher],
    tasks=[task],
    manager_agent=manager,
    process=Process.hierarchical,
    verbose=True
)
inputs = {
    'prompt': 'como se puede aprovechar la ia segun este video',
    'video_url': 'https://www.youtube.com/watch?v=rHUfF5lyRPc'
}
# Start the crew's work
result = crew.kickoff(inputs=inputs)
print(result)