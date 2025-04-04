import requests

# URL de la API
url = "http://127.0.0.1:5000/chat"

# Datos en formato JSON
data = {
    "user_id": "123",
    "user_message": "¿Qué es una metodología ágil?",
    "curso": "Gestión de proyectos"
}

# Enviar solicitud POST con JSON
response = requests.post(url, json=data, headers={"Content-Type": "application/json"})

# Mostrar respuesta del servidor
print("Código de respuesta:", response.status_code)
print("Respuesta del servidor:", response.json())
