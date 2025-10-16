
import os
import re
import requests
from PIL import Image
import streamlit as st
from pdf2image import convert_from_path

# API OCR.Space
OCR_API_KEY = "helloworld"  # Puedes reemplazar con tu propia clave gratuita
OCR_API_URL = "https://api.ocr.space/parse/image"

def extraer_texto_ocr_space(imagen):
    with open(imagen, 'rb') as img_file:
        response = requests.post(
            OCR_API_URL,
            files={"file": img_file},
            data={"apikey": OCR_API_KEY, "language": "spa"}
        )
    resultado = response.json()
    if resultado.get("IsErroredOnProcessing"):
        return ""
    return resultado["ParsedResults"][0]["ParsedText"]

def buscar_palabra_en_archivos(ruta_carpeta, palabra_clave):
    resultados = []

    for archivo in os.listdir(ruta_carpeta):
        ruta_archivo = os.path.join(ruta_carpeta, archivo)
        texto_extraido = ""

        # Archivos de texto
        if archivo.lower().endswith('.txt'):
            try:
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    texto_extraido = f.read()
            except:
                continue

        # Imágenes
        elif archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            texto_extraido = extraer_texto_ocr_space(ruta_archivo)

        # PDFs escaneados
        elif archivo.lower().endswith('.pdf'):
            try:
                paginas = convert_from_path(ruta_archivo)
                for i, pagina in enumerate(paginas):
                    temp_img = f"temp_page_{i}.jpg"
                    pagina.save(temp_img, 'JPEG')
                    texto_extraido += "
" + extraer_texto_ocr_space(temp_img)
                    os.remove(temp_img)
            except:
                continue

        if re.search(palabra_clave, texto_extraido, re.IGNORECASE):
            resultados.append(archivo)

    return resultados

# Interfaz Streamlit
st.title("Buscador de palabras clave en archivos")
ruta_carpeta = st.text_input("📁 Ruta de la carpeta:")
palabra_clave = st.text_input("🔍 Palabra clave a buscar:")

if st.button("Buscar"):
    if not os.path.isdir(ruta_carpeta):
        st.error("La ruta ingresada no es válida.")
    elif not palabra_clave:
        st.warning("Ingresa una palabra clave.")
    else:
        encontrados = buscar_palabra_en_archivos(ruta_carpeta, palabra_clave)
        if encontrados:
            st.success("Se encontró la palabra en los siguientes archivos:")
            for archivo in encontrados:
                st.write(f"- {archivo}")
        else:
            st.info("No se encontró la palabra en ningún archivo.")
