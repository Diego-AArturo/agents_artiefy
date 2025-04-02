import requests

# URL de la API
url = "http://127.0.0.1:5000/root_courses"

# Datos en formato JSON
data = {
    "prompt": "desarrollo de videojuegos"
}


# Enviar solicitud POST con JSON
response = requests.post(url, json=data, headers={"Content-Type": "application/json"})

# Mostrar respuesta del servidor
print("Código de respuesta:", response.status_code)
print("Respuesta del servidor:", response.json())
