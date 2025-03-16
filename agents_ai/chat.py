
from langchain.memory import ChatMessageHistory
import sqlite3
import json
from config import chat
from langchain.memory import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage, SystemMessage

# Inicializar modelo de chat


# Conectar a la base de datos
conn = sqlite3.connect("chatbot.db", check_same_thread=False)  # Permite acceso desde múltiples hilos
cursor = conn.cursor()

# Crear tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        user_id TEXT PRIMARY KEY,
        messages TEXT
    )
""")
conn.commit()

def get_user_memory(user_id):
    """Carga el historial de un usuario desde la base de datos de forma segura."""
    cursor.execute("SELECT messages FROM user_sessions WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if row and row[0]:  # Verifica que haya datos
        try:
            messages = json.loads(row[0])  # Convertir de JSON a lista de mensajes
        except json.JSONDecodeError:
            messages = []  # Si hay un error en la conversión, se usa una lista vacía
    else:
        messages = []

    return ChatMessageHistory(messages=[HumanMessage(content=m["human"]) if "human" in m else AIMessage(content=m["ai"]) for m in messages])

def save_user_memory(user_id, memory):
    """Guarda el historial del usuario en la base de datos."""
    messages = [{"human": msg.content} if isinstance(msg, HumanMessage) else {"ai": msg.content} for msg in memory.messages]
    messages_str = json.dumps(messages)  # Convertir a JSON seguro

    cursor.execute("REPLACE INTO user_sessions (user_id, messages) VALUES (?, ?)", (user_id, messages_str))
    conn.commit()

def chat_with_user(user_id, user_message, curso):
    """Maneja la conversación con el usuario y almacena el historial."""
    memory = get_user_memory(user_id)

    # Agregar el mensaje del usuario
    memory.add_user_message(user_message)

    # Crear contexto de conversación con un mensaje del sistema
    messages = [SystemMessage(content=f"Eres un profesor de {curso} con experiencia en desarrollo de proyectos.")]
    messages.extend(memory.messages)  # Añadir historial de usuario

    # Generar respuesta del modelo
    response = chat(messages)

    # Agregar respuesta del chatbot al historial
    memory.add_ai_message(response.content)

    # Guardar historial actualizado en la base de datos
    save_user_memory(user_id, memory)

    return response.content

