import sqlite3
import json

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config import chat
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
    try:
        cursor.execute("SELECT messages FROM user_sessions WHERE user_id=?", (user_id,))
        row = cursor.fetchone()

        if row is None or row[0] in [None, "", "null"]:
            return ChatMessageHistory(messages=[])

        raw_data = row[0]  # Datos originales en la BD
        print(f"Datos crudos desde la BD ({user_id}): {raw_data}")  # Debug

        try:
            messages = json.loads(raw_data)  # Convertir JSON a lista de mensajes
        except json.JSONDecodeError:
            print(f"Error de JSON en {user_id}, intentando corregir...")
            messages = []

        return ChatMessageHistory(
            messages=[
                HumanMessage(content=m["content"]) if m["type"] == "human" else AIMessage(content=m["content"])
                for m in messages
            ]
        )

    except sqlite3.Error as e:
        print(f"Error en la base de datos: {e}")
        return ChatMessageHistory(messages=[])

def save_user_memory(user_id, memory):
    """Guarda el historial del usuario en la base de datos."""
    messages = [{"human": msg.content} if isinstance(msg, HumanMessage) else {"ai": msg.content} for msg in memory.messages]
    messages = [
            {"type": "human", "content": msg.content} if isinstance(msg, HumanMessage) else 
            {"type": "ai", "content": msg.content}
            for msg in memory.messages
        ]
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

