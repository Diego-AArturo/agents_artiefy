import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.memory import MemoryManager
from config import chat

def chat_with_user(user_id, user_message, curso):
    agent_id = "chat"
    context = f"Eres un profesor de {curso} con experiencia en desarrollo de proyectos."

    memory_manager = MemoryManager(user_id, agent_id)
    memory_manager.add_user_message(user_message)

    messages = memory_manager.get_messages_with_context(context)
    response = chat(messages)

    memory_manager.add_ai_message(response.content)
    memory_manager.save()

    return response.content