from flask import Flask, request, jsonify
from flask_cors import CORS
from agents_ai.proyect import crew as project_crew
from agents_ai.root_class import crew_class as courses_crew
from agents_ai.clases import classes_crew
from agents_ai.chat import chat_with_user 
from tools.memory import get_history
import json

app = Flask(__name__)
CORS(app)

# Ruta para Crew de planificación de proyectos
@app.route("/plan_project", methods=["POST"])
def plan_project():
    try:
        data = request.json  
        result = project_crew.kickoff(inputs=data)  # Ejecuta el Crew de planificación
        return jsonify(result.pydantic.dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para Crew de búsqueda de cursos
@app.route("/root_courses", methods=["POST"])
def search_courses():
    try:
        data = request.json  
        result = courses_crew.kickoff(inputs=data)  # Ejecuta el Crew de búsqueda de cursos
        raw_dict = json.loads(result.raw)
        courses = raw_dict.get("courses", [])

        return jsonify({"result": courses}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para obtener información de las clases
@app.route("/get_classes", methods=["POST"])
def get_classes():
    try:
        data = request.json

        user_id = data.get("user_id")
        curso = data.get("curso")
        prompt = data.get("prompt")

        if not user_id or not curso or not prompt:
            return jsonify({"error": "Faltan campos requeridos: 'user_id', 'curso' y 'prompt'"}), 400

        # El input que espera classes_crew
        inputs = {
            "curso": curso,
            "prompt": prompt
        }

        result = classes_crew(user_id=user_id, data=inputs)
        return jsonify({"result": result}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json  
        if not all(key in data for key in ["user_id", "user_message", "curso"]):
            return jsonify({"error": "Faltan parámetros en la solicitud. Se requieren: user_id, user_message, curso"}), 400

        # Extraer valores de data
        user_id = data["user_id"]
        user_message = data["user_message"]
        curso = data["curso"]

        # Llamar a la función correctamente con los parámetros esperados
        result = chat_with_user(user_id, user_message, curso)

        return jsonify({"result": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/history", methods=["POST"])
def get_chat_history():
    try:
        data = request.json
        user_id = data.get("user_id")
        agent_id = data.get("agent_id")

        if not user_id or not agent_id:
            return jsonify({"error": "Faltan campos requeridos: 'user_id' y 'agent_id'"}), 400

        history = get_history(user_id, agent_id)
        return jsonify({"history": history}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Ruta de prueba para verificar conexión
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
