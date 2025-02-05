# Proyecto de Gestión de Tareas y Análisis de Contenido

## Descripción

Este proyecto utiliza la biblioteca `crewai` para gestionar tareas y analizar contenido de videos de YouTube y documentos PDF. El objetivo principal es desglosar proyectos en tareas accionables, estimar recursos y tiempos, y asignar tareas a los miembros del equipo de manera eficiente.

## Funcionalidades

- **Análisis de Videos de YouTube**: Extrae información clave de videos de YouTube basándose en un prompt proporcionado.
- **Análisis de Documentos PDF**: Responde preguntas basadas en la información contenida en documentos PDF.
- **Gestión de Proyectos**: Desglosa proyectos en tareas individuales, estima recursos y tiempos, y asigna tareas a los miembros del equipo.
- **Asignación de Recursos**: Optimiza la asignación de tareas según las habilidades y disponibilidad de los miembros del equipo.

## Requisitos

- Python 3.8 o superior
- Bibliotecas Python:
  - `crewai`
  - `dotenv`
  - `pydantic`

## Instalación

1. Clona el repositorio:
   ```sh
   git clone https://github.com/tu_usuario/tu_repositorio.git
   cd tu_repositorio
   ```


2. Crea un entorno virtual e instala las dependencias:

   ```python
   `source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Configura las variables de entorno en un archivo [.env](vscode-file://vscode-app/c:/Users/Diego%20Alejandro/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html):

   **``api_gemini=tu_clave_de_api_de_gemini``**

## Uso

1. Asegúrate de que las variables de entorno estén configuradas correctamente en el archivo [.env](vscode-file://vscode-app/c:/Users/Diego%20Alejandro/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html).
2. Ejecuta el script principal:

   **python** **main.py**

## Estructura del Código

* **Carga de Claves API** : Se cargan las claves API de Gemini y Google desde el archivo [.env](vscode-file://vscode-app/c:/Users/Diego%20Alejandro/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html).
* **Creación de LLM** : Se crea una instancia de [LLM](vscode-file://vscode-app/c:/Users/Diego%20Alejandro/AppData/Local/Programs/Microsoft%20VS%20Code/resources/app/out/vs/code/electron-sandbox/workbench/workbench.html) utilizando la clave API de Gemini.
* **Creación de Herramientas** : Se configuran las herramientas para el análisis de videos de YouTube y documentos PDF.
* **Definición de Agentes** : Se definen varios agentes con roles específicos, como investigador de contenido, asesor general, planificador de proyectos, analista de estimaciones y estratega de asignación.
* **Definición de Tareas** : Se definen las tareas para desglosar proyectos, estimar recursos y tiempos, y asignar tareas.
* **Gestión de Proyectos** : Se crea un agente de gestión de proyectos para coordinar las tareas del equipo.
* **Ejecución del Proyecto** : Se inicia el trabajo del equipo con las entradas proporcionadas.
