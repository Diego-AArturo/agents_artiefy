import sqlite3
import json

from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.schema import HumanMessage, AIMessage, SystemMessage


conn = sqlite3.connect("chatbot.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        user_id TEXT,
        agent_id TEXT,
        messages TEXT,
        PRIMARY KEY (user_id, agent_id)
    )
""")
conn.commit()

def get_user_memory(user_id, agent_id):
    """Carga el historial de un usuario y agente desde la base de datos."""
    try:
        cursor.execute("SELECT messages FROM user_sessions WHERE user_id=? AND agent_id=?", (user_id, agent_id))
        row = cursor.fetchone()

        if row is None or row[0] in [None, "", "null"]:
            return ChatMessageHistory(messages=[])

        raw_data = row[0]
        try:
            messages = json.loads(raw_data)
        except json.JSONDecodeError:
            print(f"Error de JSON en {user_id}-{agent_id}, intentando corregir...")
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


def save_user_memory(user_id, agent_id, memory):
    """Guarda el historial del usuario para un agente específico."""
    messages = [
        {"type": "human", "content": msg.content} if isinstance(msg, HumanMessage) else 
        {"type": "ai", "content": msg.content}
        for msg in memory.messages
    ]
    messages_str = json.dumps(messages)

    cursor.execute(
        "REPLACE INTO user_sessions (user_id, agent_id, messages) VALUES (?, ?, ?)",
        (user_id, agent_id, messages_str)
    )
    conn.commit()

def get_history(user_id, agent_id):
    try:
        conn = sqlite3.connect('chatbot.db')
        cursor = conn.cursor()
        cursor.execute("SELECT messages FROM user_sessions WHERE user_id=? AND agent_id=?", (user_id, agent_id))
        
        row = cursor.fetchone()
        conn.close()

        if row is None or row[0] in [None, "", "null"]:
            return []

        raw_data = row[0]
        try:
            messages = json.loads(raw_data)
        except json.JSONDecodeError:
            print(f"Error de JSON en {user_id}-{agent_id}, intentando corregir...")
            messages = []

        return messages

    except sqlite3.Error as e:
        return str(e)

class MemoryManager:
    def __init__(self, user_id, agent_id):
        self.user_id = user_id
        self.agent_id = agent_id
        self.memory = get_user_memory(user_id, agent_id)

    def add_user_message(self, content):
        self.memory.add_user_message(content)

    def add_ai_message(self, content):
        self.memory.add_ai_message(content)

    def save(self):
        save_user_memory(self.user_id, self.agent_id, self.memory)

    def get_messages_with_context(self, context):
        """Devuelve una lista de mensajes con el contexto inicial y el historial."""
        return [SystemMessage(content=context)] + self.memory.messages


