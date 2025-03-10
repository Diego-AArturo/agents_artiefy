from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from agents_ai.proyect import crew as project_crew
from agents_ai.root_class import crew_class as courses_crew
from agents_ai.clases import crew_guia_cursos as classes_crew 
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
@app.route("/search_courses", methods=["POST"])
def search_courses():
    try:
        data = request.json  
        result = courses_crew.kickoff(inputs=data)  # Ejecuta el Crew de búsqueda de cursos
        return jsonify({"result": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta para obtener información de las clases
@app.route("/get_classes", methods=["POST"])
def get_classes():
    try:
        data = request.json  
        result = classes_crew.kickoff(inputs=data)  # Ejecuta el Crew de clases
        return jsonify({"result": str(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Ruta de prueba para verificar conexión
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "API is running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
