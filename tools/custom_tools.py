import psycopg2
from crewai.tools import BaseTool
from pydantic import BaseModel
from crewai.tools import tool
import warnings
import os
import psycopg2
import requests
from pathlib import Path
from docx2pdf import convert as docx_to_pdf
import aspose.slides as slides
import pandas as pd
from openpyxl import load_workbook
from fpdf import FPDF
import shutil
from config import DOWNLOAD_FOLDER,PDF_FOLDER, DATABASE_URL, aws
warnings.filterwarnings("ignore", category=DeprecationWarning)
import sqlite3
import json



# 🔹 Función para descargar archivos desde URLs
def download_file(url: str, folder: str) -> str:
    file_name = os.path.join(folder, Path(url).name)
    try:
        response = requests.get(url)
        with open(file_name, "wb") as file:
            file.write(response.content)
        return file_name
    except Exception as e:
        print(f"Error al descargar {url}: {e}")
        return ""

# Función para convertir archivos a PDF
def convert_to_pdf(file_path: str) -> str:
    file_ext = Path(file_path).suffix.lower()
    
    output_pdf_path = os.path.join(PDF_FOLDER, f"{Path(file_path).stem}.pdf")

    try:
        if file_ext == ".docx":
            temp_pdf = file_path.replace(".docx", ".pdf")
            docx_to_pdf(file_path)
            shutil.move(temp_pdf, output_pdf_path)  # Mueve el PDF generado
            return output_pdf_path
        elif file_ext == ".xlsx":
            df = pd.read_excel(file_path)
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for i, row in df.iterrows():
                pdf.cell(200, 10, txt=str(row.values), ln=True)
            pdf.output(output_pdf_path)
            return output_pdf_path
        elif file_ext == ".pptx":
            # Convierte PowerPoint a PDF usando Aspose.Slides
            pdf_options = slides.export.PdfOptions()
            pdf_options.jpeg_quality = 90
            pdf_options.sufficient_resolution = 300
            pdf_options.save_metafiles_as_png = True
            pdf_options.text_compression = slides.export.PdfTextCompression.FLATE
            pdf_options.compliance = slides.export.PdfCompliance.PDF15

            with slides.Presentation(file_path) as presentation:
                presentation.save(output_pdf_path, slides.export.SaveFormat.PDF, pdf_options)
            return output_pdf_path
        
        elif file_ext == ".pdf":
            # Ya es un PDF, moverlo a la carpeta destino si es necesario
            shutil.copy(file_path, output_pdf_path) if file_path != output_pdf_path else None
            return output_pdf_path
        else:
            # print(f"No se puede convertir: {file_path}")
            return ""
    except Exception as e:
        # print(f"Error al procesar {file_path}: {e}")
        return ""
    


class BDSearchTool(BaseTool):
    name: str = "BD Search Tool"  
    description: str = "Busca la descripción de las clases de un curso en la base de datos PostgreSQL y devuelve datos estructurados."

    class ArgsSchema(BaseModel):
        course_name: str

    def _run(self, course_name: str) -> dict:
        """Ejecuta la consulta en la base de datos y obtiene las clases y recursos en PDF."""
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        os.makedirs(PDF_FOLDER, exist_ok=True)
        try:
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()

            cursor.execute("""
                SELECT description, resource_key, resource_names 
                FROM lessons 
                WHERE course_id IN (SELECT id FROM courses WHERE title = %s);
            """, (course_name,))

            results = cursor.fetchall()

            clases = []
            for row in results:
                descripcion = row[0]
                recurso_keys = row[1].split(',') if row[1] else []
                recurso_urls = [f"{aws}/{doc.strip()}" for doc in recurso_keys]
                nombre_recurso = row[2]

                # Descargar y convertir recursos a PDF
                pdf_resources = []
                for url in recurso_urls:
                    file_path = download_file(url, DOWNLOAD_FOLDER)
                    if file_path:
                        pdf_path = convert_to_pdf(file_path)
                        if pdf_path:
                            pdf_resources.append(pdf_path)

                clases.append({
                    "Descripcion": descripcion,
                    "Urls de Recursos": pdf_resources,
                    "Nombre de recurso": nombre_recurso
                })
            
            # Eliminar archivos temporales de "downloads"
            shutil.rmtree(DOWNLOAD_FOLDER, ignore_errors=True)
            
            return {"curso": course_name, "clases": clases}

        except Exception as e:
            print(f"❌ Error al acceder a la base de datos: {e}")
            return {"error": str(e)}

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

class CourseRootTool_names(BaseTool):
    name: str = "Course root"
    description: str = "Busca los cursos relevantes según la necesidad del usuario desde la base de datos PostgreSQL."

    def _run(self) -> str:
        try:
            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()

            query = """
                SELECT title 
                FROM courses 
                
            """
            
            cursor.execute(query)
            results = cursor.fetchall()

            if not results:
                return "Nn"

            output = "Cursos sugeridos:\n\n"
            for i, (title,) in enumerate(results, 1):
                output += f"{i}. {title}\n\n"

            return output.strip()

        except Exception as e:
            return f"Error al acceder a la base de datos: {str(e)}"

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

class CourseRootTool_descriptions(BaseTool):
    name: str = "Course root descriptions"
    description: str = "Obtiene las descripciones completas de una lista de títulos de cursos desde la base de datos."

    def _run(self, courses_names: str) -> str:
        try:
            # Convertir string plano en lista si hace falta
            titles = [t.strip() for t in courses_names.split(",") if t.strip()]

            if not titles:
                return "Nn"

            connection = psycopg2.connect(DATABASE_URL)
            cursor = connection.cursor()

            placeholders = ', '.join(['%s'] * len(titles))
            query = f"SELECT id, title, description FROM courses WHERE title IN ({placeholders})"

            cursor.execute(query, tuple(titles))
            results = cursor.fetchall()

            if not results:
                return "Nn"

            output = "Cursos seleccionados:\n\n"
            for i, (course_id, title, desc) in enumerate(results, 1):
                output += f"{i}. ID: {course_id} - {title}\nDescripción: {desc}\n\n"

            return output.strip()

        except Exception as e:
            return f"Error al acceder a la base de datos: {str(e)}"

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()
