import requests

# URL de la API
url = "http://127.0.0.1:5000/plan_project"

# Datos en formato JSON
data = {
    "project_type": "Website",
    "project_requirements": "Crear una web responsiva",
    "project_objectives": "Tener una presencia digital",
    "team_members": "Diego, Laura",
    "industry": "Tecnología"
}

# Enviar solicitud POST con JSON
response = requests.post(url, json=data, headers={"Content-Type": "application/json"})

# Mostrar respuesta del servidor
print("Código de respuesta:", response.status_code)
print("Respuesta del servidor:", response.json())
