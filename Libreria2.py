import os
from openai import OpenAI
import os
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF
import re
import statistics
import unicodedata
import requests
import xml.etree.ElementTree as ET
import pandas as pd



def normalize_text(text):
    # Normalizar quitando acentos y pasando a ASCII
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    # Convertir a minúsculas y eliminar espacios
    text = re.sub(r"\s+", "", text.lower())
    return text
# Clase coleccion de pdf
class Coleccion:
    def __init__(self, ubicacion, descripcion):
        self.n = 0  # Número de archivos en la colección
        self.ubicacion = ubicacion  # Ubicación de la carpeta con los PDFs
        self.elementos = []  # Títulos de los archivos PDF
        self.descripcion = descripcion  # Descripción de la colección
        self.tabla_historia = [
            ["Constructor", 
             f"{descripcion}. Genera las siguientes variables de salida: "
             "1) 'n': Número total de archivos en la colección. "
             "2) 'ubicacion': Ubicación de la carpeta donde se almacenan los archivos PDF. "
             "3) 'elementos': Lista de títulos de los archivos PDF. "
             "4) 'descripcion': Descripción general de la colección.", 
             "Origen"]
        ]
        self.listar_archivos()
    def listar_archivos(self):
        """Lista los archivos en la ubicación especificada y actualiza la lista de elementos."""
        # Lista todos los archivos en la ubicación especificada y los añade a la lista de elementos
        self.elementos = [archivo for archivo in os.listdir(self.ubicacion) if archivo.endswith('.pdf')]
# Interactua con chatgpt
def quest_gpt(textin):
    """
    Esta función interactúa con la API de OpenAI para generar respuestas utilizando el modelo gpt-3.5-turbo.
    
    Entrada:
    - textin: String con el contenido del mensaje que se enviará al modelo.

    Salida:
    - varout: String con la respuesta generada por el modelo.
    """
    #client = OpenAI(api_key='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')
    client = OpenAI(api_key='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX) #Aca colocar API
    
    
    
    
    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    #model="gpt-4",
    messages=[
    #{"role": "system", "content": "Toma conocimiento que David Araya es un ingeniero que trabaja en el ITISB"},
    {"role": "user", "content": textin}
    ]
    )
    choice = response.choices[0]
    varout=choice.message.content
    return varout
# Extrae contenido total
def extraer_contenido_total(coleccion):
    """
    Extrae el texto completo de cada PDF en la colección utilizando fitz (PyMuPDF) y actualiza el objeto con esta información. 
    Entrada:
    - coleccion: Objeto de la clase Coleccion que será modificado.
    """
    # Inicializar 'contenido' como lista vacía para almacenar el texto de cada PDF
    coleccion.contenido = []
    # Extraer texto de cada archivo PDF
    for archivo in coleccion.elementos:
        ruta_completa = os.path.join(coleccion.ubicacion, archivo)
        texto_documento = ""
        try:
            doc = fitz.open(ruta_completa)
            for pagina in doc:
                texto_documento += pagina.get_text("text")  # Utilizar 'text' para extraer el texto como cadena
            doc.close()  # Cerrar el documento después de procesar
            coleccion.contenido.append(texto_documento)
        except Exception as e:
            print(f"Error al leer el archivo {archivo}: {e}")
            coleccion.contenido.append("Error en la extracción de texto.")

    # Agregar registro en tabla_historia
    descripcion_rutina = "Extracción del texto completo de cada PDF en la colección utilizando fitz (PyMuPDF)."
    descripcion_variable_salida = ("Variable 'contenido' es una lista donde cada elemento contiene el texto "
                                   "extraído de un archivo PDF correspondiente.")
    coleccion.tabla_historia.append(["extraer_contenido_total", descripcion_rutina, descripcion_variable_salida])
#No funciona
#def separar_frases(coleccion):
    """
    Procesa el texto almacenado en 'contenido' para separar frases basadas en puntos seguidos y aparte.
    Actualiza el objeto con una nueva estructura que almacena las frases separadas.
    
    Entrada:
    - coleccion: Objeto de la clase Coleccion que será modificado.
    """
    # Inicializar 'separa_frases' como lista vacía para almacenar las frases de cada PDF
    coleccion.separa_frases = []

    # Procesar cada texto de PDF almacenado en 'contenido'
    for texto in coleccion.contenido:
        frases = []
        punto_aparte_indices = []
        inicio = 0  # Inicio de la frase actual

        # Encontrar todas las frases en el texto
        for i, caracter in enumerate(texto):
            if caracter == '.':
                if i + 1 < len(texto) and texto[i + 1] == '\n':  # Chequear punto aparte
                    frases.append(texto[inicio:i + 1].strip())
                    punto_aparte_indices.append(len(frases) - 1)
                    inicio = i + 2
                else:
                    frases.append(texto[inicio:i + 1].strip())
                    inicio = i + 2

        # Agregar las frases y los índices de punto aparte al objeto colección
        coleccion.separa_frases.append({
            'valor': frases,
            'punto_aparte': punto_aparte_indices
        })

    # Agregar registro en tabla_historia
    descripcion_rutina = "Separación de frases del texto completo de cada PDF en la colección."
    descripcion_variable_salida = ("Variable 'separa_frases' es una lista donde cada elemento contiene una matriz "
                                   "de frases y una lista de índices donde las frases terminan en punto aparte.")
    coleccion.tabla_historia.append(["separar_frases", descripcion_rutina, descripcion_variable_salida])
def separar_por_lineas(coleccion):
    """
    Crea una estructura de lista de listas donde cada sublista contiene las líneas de un documento específico.
    
    Entrada:
    - coleccion: Objeto de la clase Coleccion que contiene el atributo 'contenido'.
    
    Salida:
    - Modifica el objeto coleccion agregando un nuevo atributo 'contenido_linea'.
    """
    coleccion.contenido_linea = []

    for texto in coleccion.contenido:
        # Divide el texto en líneas y elimina líneas vacías
        lineas = [linea for linea in texto.split('\n') if linea.strip()]
        coleccion.contenido_linea.append(lineas)

    # Agregar un registro a la tabla_historia para documentar la operación
    descripcion_rutina = "Separación del contenido de cada documento en líneas."
    descripcion_variable_salida = "Variable 'contenido_linea' contiene las líneas de texto de cada documento."
    coleccion.tabla_historia.append(["separar_por_lineas", descripcion_rutina, descripcion_variable_salida])
def extraer_capitulos_gpt(coleccion):  
    """
    Utiliza GPT-3.5-turbo para identificar y formatear los capítulos del contenido de cada PDF.
    
    Entrada:
    - coleccion: Objeto de la clase Coleccion que será modificado.
    """
    coleccion.capitulos = []

    for texto in coleccion.contenido:
        # Crear un prompt para GPT
        prompt = f"Por favor, enumera los capítulos para el siguiente texto, usando el formato '1. Título del Capítulo 2. Título del Capítulo':\n\n{texto}"

        # Usar la función quest_gpt para obtener la respuesta de GPT
        resultado_gpt = quest_gpt(prompt)

        # Parsear la respuesta para extraer los capítulos
        # Utilizar una expresión regular para extraer los capítulos
        # Asumiendo que el formato es '1. Título 2. Título'
        capitulos = []
        # Dividir primero por líneas para aislar cada numeración
        for line in resultado_gpt.splitlines():
            match = re.match(r"(\d+)\.\s(.+)", line.strip())
            if match:
                capitulos.append(match.group(2))

        # Agregar los capítulos parseados al objeto coleccion
        coleccion.capitulos.append(capitulos)

    # Agregar registro en tabla_historia
    descripcion_rutina = "Extracción de capítulos usando GPT."
    descripcion_variable_salida = "Variable 'capitulos' contiene los capítulos identificados y formateados por GPT."
    coleccion.tabla_historia.append(["extraer_capitulos_gpt", descripcion_rutina, descripcion_variable_salida])
def extraer_capitulos_patron(coleccion):
    # Patrones típicos para títulos de capítulos
    patrones = [
        r'\b(\d+)\.\s+([^\n]+)',  # Números seguidos de un punto y espacio, ej. "1. Introduction"
        r'\b([A-Z])\.\s+([^\n]+)'  # Letras mayúsculas seguidas de un punto y espacio, ej. "A. Background"
    ]

    # Inicializar la estructura de datos para almacenar información de capítulos
    coleccion.capitulos = {}

    # Procesar cada documento
    for index, lineas_documento in enumerate(coleccion.contenido_linea):
        coleccion.capitulos[index] = {'capitulos': []}
        capitulo_actual = None

        # Iterar sobre cada línea del documento
        for i, linea in enumerate(lineas_documento):
            for patron in patrones:
                match = re.match(patron, linea)
                if match:
                    if capitulo_actual:  # Si ya hay un capítulo en proceso, cerrarlo
                        capitulo_actual['linea_termino'] = i - 1
                        coleccion.capitulos[index]['capitulos'].append(capitulo_actual)

                    # Comenzar un nuevo capítulo
                    capitulo_actual = {
                        'nombre': f"{match.group(1)}. {match.group(2)}",
                        'linea_inicio': i,
                        'linea_termino': None  # Se actualizará cuando encuentre el próximo capítulo o finalice el documento
                    }

        # Cerrar el último capítulo si aún está abierto al final del documento
        if capitulo_actual and capitulo_actual['linea_termino'] is None:
            capitulo_actual['linea_termino'] = len(lineas_documento) - 1
            coleccion.capitulos[index]['capitulos'].append(capitulo_actual)

    # Agregar un registro en tabla_historia para documentar esta operación
    descripcion_rutina = "Extracción de capítulos utilizando patrones específicos, procesados línea por línea."
    descripcion_variable_salida = "Variable 'capitulos' contiene información detallada de los capítulos identificados en cada documento."
    coleccion.tabla_historia.append(["extraer_capitulos_patron", descripcion_rutina, descripcion_variable_salida])
def extraer_contenido_total_porlinea(coleccion, indices=None):
    """
    Extrae el texto de cada PDF en la colección por línea y por tramo (span) utilizando fitz (PyMuPDF),
    almacenando también el tamaño de letra y tipo de letra.
    
    Entrada:
    - coleccion: Objeto de la clase Coleccion que será modificado.
    - indices: Lista opcional de índices (basados en 1) de documentos específicos para procesar.
    """
    coleccion.contenido_porlinea = []

    # Determinar los índices de los documentos a procesar
    if indices is None:
        indices = range(len(coleccion.elementos))

    for i in indices:
        archivo = coleccion.elementos[i]
        ruta_completa = os.path.join(coleccion.ubicacion, archivo)
        documento_texto = {'linea': []}  # Diccionario para almacenar líneas y tramos

        try:
            doc = fitz.open(ruta_completa)
            for pagina in doc:
                contenido_pagina = pagina.get_text("dict")
                for bloque in contenido_pagina['blocks']:
                    if bloque['type'] == 0:  # Solo procesar bloques de texto
                        for linea in bloque['lines']:
                            linea_info = {'tramo': []}
                            for span in linea['spans']:
                                tramo = {
                                    'texto': span['text'],
                                    'tamaño': span['size'],
                                    'fuente': span['font']
                                }
                                linea_info['tramo'].append(tramo)
                            documento_texto['linea'].append(linea_info)
            doc.close()
            coleccion.contenido_porlinea.append(documento_texto)
        except Exception as e:
            print(f"Error al leer el archivo {archivo}: {e}")
            coleccion.contenido_porlinea.append("Error en la extracción de texto.")

    # Agregar registro en tabla_historia
    descripcion_rutina = "Extracción del texto por línea y por tramo, incluyendo detalles del formato, utilizando fitz (PyMuPDF)."
    descripcion_variable_salida = ("Variable 'contenido_porlinea' organiza el texto por documentos, líneas y tramos, con detalles del formato.")
    coleccion.tabla_historia.append(["extraer_contenido_total_porlinea", descripcion_rutina, descripcion_variable_salida])
def extraer_capitulos_patron3(coleccion):
    # Diccionario de términos y sinónimos (en inglés)
    diccionario = {
        0: ["Introduction"],
        1: ["Methodology", "Methods"],
        2: ["Results", "R E S U L T S"],
        3: ["Discussion","CONCLUSION AND FUTURE WORK"],
        4: ["Bibliography", "References"]
    }
    
    # Inicializar la estructura para almacenar los capítulos y los resultados
    coleccion.var_extraer_capitulos_patron3 = {
        'capitulos': [],
        'encontrados': []
    }
    
    # Procesar cada documento
    for index, documento in enumerate(coleccion.contenido_porlinea):
        capitulos_del_documento = {'nombre': []}
        todos_encontrados = True  # Para verificar si todos los términos fueron encontrados
        
        # Buscar cada término y sus sinónimos
        for linea_info in documento['linea']:
            texto_linea = " ".join(tramo['texto'] for tramo in linea_info['tramo'])
            for terminos in diccionario.values():
                for termino in terminos:
                    # Verifica que el término esté precedido por un salto de línea dentro de los últimos cinco caracteres antes del término
                    if re.search(rf"(.{{0,5}}\n)?\s*{termino}\s*$", texto_linea, re.IGNORECASE):
                        capitulos_del_documento['nombre'].append(texto_linea.strip())
                        break
                else:
                    # Si no se encuentra el término, se continúa con el siguiente
                    continue
                # Si se encuentra el término, no buscar más en esta línea
                break
            else:
                # Si no se encontró ningún término en la línea, marcar como no todos encontrados
                todos_encontrados = False

        # Agregar a la colección de capítulos
        coleccion.var_extraer_capitulos_patron3['capitulos'].append(capitulos_del_documento)
        coleccion.var_extraer_capitulos_patron3['encontrados'].append(1 if todos_encontrados else 0)

    # Agregar registro en tabla_historia
    descripcion_rutina = "Búsqueda flexible de términos clave para identificar capítulos con consideración de contexto cercano."
    descripcion_variable_salida = "Variable 'var_extraer_capitulos_patron3' contiene los capítulos identificados y los indicadores de completitud."
    coleccion.tabla_historia.append(["extraer_capitulos_patron3", descripcion_rutina, descripcion_variable_salida])
def extrae_capitulos_tamaño(coleccion):
    # Inicializar la variable de salida directamente como una lista
    capitulos_tamaño = []
    for index_documento, documento in enumerate(coleccion.contenido_porlinea):
        tamaños_muestra = [tramo['tamaño'] for linea in documento['linea'] for tramo in linea['tramo']]
        fuentes_muestra = [tramo['fuente'] for linea in documento['linea'] for tramo in linea['tramo']]
        tamaño_normal = statistics.mode(tamaños_muestra)
        fuente_normal = statistics.mode(fuentes_muestra)
        tamaños_intro = []
        fuentes_intro = []
        for linea in documento['linea'][:300]:
            for tramo in linea['tramo']:
                texto_normalizado = normalize_text(tramo['texto'])
                if 'introduction' in texto_normalizado:
                    tamaños_intro.append(tramo['tamaño'])
                    fuentes_intro.append(tramo['fuente'])
        if tamaños_intro:
            tamaño_intro = max(tamaños_intro)
        else:
            # Imprimir detalles del documento actual para revisión
            print(f"Documento {index_documento} no contiene 'Introduction' en las primeras 300 líneas.")
            print("Pulse enter para continuar...")
            input()  # Pausar la ejecución para permitir revisión manual



        fuente_intro = max(set(fuentes_intro), key=fuentes_intro.count) 
        umbral_tamaño = abs(tamaño_intro - tamaño_normal) / 3
        if umbral_tamaño < 0.1 * tamaño_intro:
            umbral_tamaño = 0.1 * tamaño_intro
        frases_importantes = []
        for linea in documento['linea']:
            for tramo in linea['tramo']:
                condicion_tamaño = (tamaño_intro - umbral_tamaño) < tramo['tamaño'] < (tamaño_intro + umbral_tamaño)
                condicion_salto = len(linea['tramo']) == 1  # Solo un tramo en la línea indica un posible salto de línea después
                if condicion_tamaño and condicion_salto:
                    frases_importantes.append(tramo['texto'])
        # Evaluar el número de frases importantes identificadas
        if len(frases_importantes) > 200:
            frases_importantes = []
            for linea in documento['linea']:
                for tramo in linea['tramo']:
                    condicion_tamaño = (tamaño_intro - umbral_tamaño) < tramo['tamaño'] < (tamaño_intro + umbral_tamaño)
                    condicion_salto = len(linea['tramo']) == 1  # Solo un tramo en la línea indica un posible salto de línea después
                    condicion_fuente = tramo['fuente'] != fuente_normal and tramo['fuente'] == fuente_intro
                    if condicion_tamaño and condicion_fuente and condicion_salto:
                        frases_importantes.append(tramo['texto']) 
        # Añadir los títulos extraídos al índice correspondiente en la lista
        capitulos_tamaño.append(frases_importantes)
    # Almacenar la variable de salida en la colección de documentos
    coleccion.capitulos_tamaño = capitulos_tamaño
    descripcion_rutina = "Extracción de títulos basada en tamaño y tipo de fuente, incluyendo condiciones de formato de línea."
    descripcion_variable_salida = "Variable 'capitulos_tamaño' contiene listas de títulos identificados para cada documento."
    coleccion.tabla_historia.append(["extrae_capitulos_tamaño", descripcion_rutina, descripcion_variable_salida])
def crea_contenido_pubmedfile(filepath):
    # Inicializar la lista para almacenar los datos extraídos
    contenido_pubmed = []
    
    # Leer el contenido del archivo
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()
    
    # Variables temporales para almacenar información de cada artículo
    current_article = {}
    
    for line in lines:
        # Extraer PMID
        if line.startswith('PMID- '):
            current_article['PMID'] = line.split('- ')[1].strip()
        
        # Extraer DOI
        elif line.startswith('LID - ') and '[doi]' in line:
            current_article['DOI'] = line.split(' [doi]')[0].split('- ')[1].strip()
        
        # Extraer título del artículo
        elif line.startswith('TI  - '):
            title = line.split('- ')[1].strip()
            # Continuar extrayendo el título si se extiende a múltiples líneas
            while True:
                next_line_index = lines.index(line) + 1
                if not lines[next_line_index].startswith('      '): break
                title += ' ' + lines[next_line_index].strip()
                line = lines[next_line_index]
            current_article['Title'] = title
        
        # Extraer Abstract
        elif line.startswith('AB  - '):
            abstract = line.split('- ')[1].strip()
            # Continuar extrayendo el abstract si se extiende a múltiples líneas
            while True:
                next_line_index = lines.index(line) + 1
                if not lines[next_line_index].startswith('      '): break
                abstract += ' ' + lines[next_line_index].strip()
                line = lines[next_line_index]
            current_article['Abstract'] = abstract

        # Guardar y reiniciar para el próximo artículo al encontrar una línea vacía
        if line == '':
            if current_article:
                # Asegurarse de que todos los campos requeridos están presentes
                if all(key in current_article for key in ['PMID', 'DOI', 'Title', 'Abstract']):
                    contenido_pubmed.append([
                        current_article['Title'],
                        current_article['DOI'],
                        current_article['PMID'],
                        current_article['Abstract']
                    ])
                # Reiniciar el diccionario para el siguiente artículo
                current_article = {}
    
    return contenido_pubmed
def pmc_download(pmid):
    """
    Descarga el contenido de un artículo de PubMed Central (PMC) dado su PMID en formato XML.
    Extrae las secciones del artículo de acuerdo con los nombres de secciones observadas (TITLE, ABSTRACT, INTRO, METHODS, RESULTS, DISCUSS, etc.)
    
    Entrada:
    - pmid: Identificador de PubMed (PMID).

    Salida:
    - paper: Diccionario con las secciones del artículo extraídas (Introduction, Methods, Results, Discussion, Conclusion).
    """
    # Solicitar el contenido XML del artículo
    url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmid}/unicode'
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa
    if response.status_code != 200:
        print(f"Error al descargar el artículo con PMID {pmid}. Código de estado: {response.status_code}")
        return {
            "Introduction": '',
            "Methods": '',
            "Results": '',
            "Discussion": '',
            "Conclusion": ''
        }

    # Verificar si el contenido de la respuesta es válido y no está vacío
    if not response.text.strip():
        print(f"El contenido del artículo con PMID {pmid} está vacío o no es válido.")
        return {
            "Introduction": '',
            "Methods": '',
            "Results": '',
            "Discussion": '',
            "Conclusion": ''
        }

    try:
        # Parsear el XML de la respuesta
        root = ET.fromstring(response.text)
    except ET.ParseError as e:
        print(f"Error al parsear el XML para PMID {pmid}. Detalles del error: {e}")
        return {
            "Introduction": '',
            "Methods": '',
            "Results": '',
            "Discussion": '',
            "Conclusion": ''
        }

    # Inicializar un diccionario para las secciones clave
    paper = {
        "Introduction": '',
        "Methods": '',
        "Results": '',
        "Discussion": '',
        "Conclusion": ''
    }

    # Mapeo de etiquetas observadas a secciones
    section_map = {
        "INTRO": "Introduction",
        "METHODS": "Methods",
        "RESULTS": "Results",
        "DISCUSS": "Discussion",
        "CONCLUSION": "Conclusion"  # Si no existe, dejará vacío
    }

    # Extraer los textos de las secciones
    for passage in root.findall('./document/passage'):
        passage_type_element = passage.find('./infon[@key="section_type"]')
        passage_text_element = passage.find('./text')
        
        # Verificar que ambos elementos existen
        if passage_type_element is not None and passage_text_element is not None:
            passage_type = passage_type_element.text.upper()
            passage_text = passage_text_element.text

            # Mapear la etiqueta observada a la sección correspondiente
            if passage_type in section_map:
                section_name = section_map[passage_type]
                paper[section_name] += '\n' + passage_text

    # Devolver el diccionario con las secciones clave
    return paper

    """
    Descarga el contenido de un artículo de PubMed Central (PMC) dado su PMID en formato XML.
    Extrae las secciones del artículo (Introduction, Methods, Results, Discussion, Conclusion)
    y devuelve un diccionario con esas secciones.

    Entrada:
    - pmid: Identificador de PubMed (PMID).

    Salida:
    - paper: Diccionario con las secciones del artículo extraídas.
    """
    # Solicitar el contenido XML del artículo
    url = f'https://www.ncbi.nlm.nih.gov/research/bionlp/RESTful/pmcoa.cgi/BioC_xml/{pmid}/unicode'
    response = requests.get(url)

    # Verificar si la solicitud fue exitosa
    if response.status_code != 200:
        print(f"Error al descargar el artículo con PMID {pmid}. Código de estado: {response.status_code}")
        return {
            "Introduction": '',
            "Methods": '',
            "Results": '',
            "Discussion": '',
            "Conclusion": ''
        }
    
    # Verificar si el contenido de la respuesta es válido y no está vacío
    if not response.text.strip():
        print(f"El contenido del artículo con PMID {pmid} está vacío o no es válido.")
        return {
            "Introduction": '',
            "Methods": '',
            "Results": '',
            "Discussion": '',
            "Conclusion": ''
        }

    try:
        # Parsear el XML de la respuesta
        root = ET.fromstring(response.text)
    except ET.ParseError as e:
        print(f"Error al parsear el XML para PMID {pmid}. Detalles del error: {e}")
        return {
            "Introduction": '',
            "Methods": '',
            "Results": '',
            "Discussion": '',
            "Conclusion": ''
        }

    # Inicializar un diccionario para las secciones clave
    paper = {
        "Introduction": '',
        "Methods": '',
        "Results": '',
        "Discussion": '',
        "Conclusion": ''
    }

    # Extraer los textos de las secciones
    for passage in root.findall('./document/passage'):
        passage_type_element = passage.find('./infon[@key="section_type"]')
        passage_text_element = passage.find('./text')
        
        # Verificar que ambos elementos existen
        if passage_type_element is not None and passage_text_element is not None:
            passage_type = passage_type_element.text.lower()
            passage_text = passage_text_element.text

            # Asignar el texto de la sección según su tipo
            if 'introduction' in passage_type:
                paper['Introduction'] += '\n' + passage_text
            elif 'methods' in passage_type:
                paper['Methods'] += '\n' + passage_text
            elif 'results' in passage_type:
                paper['Results'] += '\n' + passage_text
            elif 'discussion' in passage_type:
                paper['Discussion'] += '\n' + passage_text
            elif 'conclusion' in passage_type or 'conclusions' in passage_type:
                paper['Conclusion'] += '\n' + passage_text

    # Devolver el diccionario con las secciones clave
    return paper

    # Inicializar la lista para almacenar los datos extraídos
    contenido_pubmed = []
    
    # Leer el contenido del archivo
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()
    
    # Variables temporales para almacenar información de cada artículo
    current_article = {}
    
    for line in lines:
        # Extraer PMID
        if line.startswith('PMID- '):
            current_article['PMID'] = line.split('- ')[1].strip()
        
        # Extraer DOI
        elif line.startswith('LID - ') and '[doi]' in line:
            current_article['DOI'] = line.split(' [doi]')[0].split('- ')[1].strip()
        
        # Extraer título del artículo
        elif line.startswith('TI  - '):
            title = line.split('- ')[1].strip()
            # Continuar extrayendo el título si se extiende a múltiples líneas
            while True:
                next_line_index = lines.index(line) + 1
                if not lines[next_line_index].startswith('      '): break
                title += ' ' + lines[next_line_index].strip()
                line = lines[next_line_index]
            current_article['Title'] = title
        
        # Extraer Abstract
        elif line.startswith('AB  - '):
            abstract = line.split('- ')[1].strip()
            # Continuar extrayendo el abstract si se extiende a múltiples líneas
            while True:
                next_line_index = lines.index(line) + 1
                if not lines[next_line_index].startswith('      '): break
                abstract += ' ' + lines[next_line_index].strip()
                line = lines[next_line_index]
            current_article['Abstract'] = abstract

        # Guardar y reiniciar para el próximo artículo al encontrar una línea vacía
        if line == '':
            if current_article:
                # Asegurarse de que todos los campos requeridos están presentes
                if all(key in current_article for key in ['PMID', 'DOI', 'Title', 'Abstract']):
                    contenido_pubmed.append([
                        current_article['Title'],
                        current_article['DOI'],
                        current_article['PMID'],
                        current_article['Abstract']
                    ])
                # Reiniciar el diccionario para el siguiente artículo
                current_article = {}
    
    return contenido_pubmed
def pmc_to_datos_pubmed2(datos_pubmed):
    """
    Esta función recibe la tabla 'datos_pubmed' con la información básica de artículos (Título, DOI, PMID, Resumen),
    descarga el contenido del artículo desde PubMed Central usando el PMID, extrae las secciones clave
    (Introduction, Methods, Results, Discussion, Conclusion) y genera una nueva tabla 'datos_pubmed2' con esos
    campos adicionales.

    Entrada:
    - datos_pubmed: Tabla existente con columnas [Título, DOI, PMID, Resumen].

    Salida:
    - datos_pubmed2: Nueva tabla con las mismas columnas de 'datos_pubmed' y las columnas adicionales
      [Introduction, Methods, Results, Discussion, Conclusion].
    """
    # Lista para almacenar los datos enriquecidos
    datos_pubmed2 = []

    # Iterar sobre cada fila de la tabla 'datos_pubmed'
    for row in datos_pubmed:
        title, doi, pmid, abstract = row

        # Descargar las secciones clave del artículo usando el PMID
        paper_sections = pmc_download(pmid)

        # Crear una nueva fila con las secciones adicionales
        new_row = [
            title, doi, pmid, abstract, 
            paper_sections['Introduction'].strip(), 
            paper_sections['Methods'].strip(), 
            paper_sections['Results'].strip(), 
            paper_sections['Discussion'].strip(), 
            paper_sections['Conclusion'].strip()
        ]

        # Añadir la nueva fila a la tabla 'datos_pubmed2'
        datos_pubmed2.append(new_row)

    # Crear un DataFrame con las columnas enriquecidas
    datos_pubmed2_df = pd.DataFrame(datos_pubmed2, columns=[
        'Title', 'DOI', 'PMID', 'Abstract', 
        'Introduction', 'Methods', 'Results', 'Discussion', 'Conclusion'
    ])

    return datos_pubmed2_df

    # Inicializar la lista para almacenar los datos extraídos
    contenido_pubmed = []

    # Leer el contenido del archivo
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()

    # Variables temporales para almacenar información de cada artículo
    current_article = {}

    for line in lines:
        # Extraer PMID
        if line.startswith('PMID- '):
            current_article['PMID'] = line.split('- ')[1].strip()
        
        # Extraer DOI
        elif line.startswith('LID - ') and '[doi]' in line:
            current_article['DOI'] = line.split(' [doi]')[0].split('- ')[1].strip()
        
        # Extraer título del artículo
        elif line.startswith('TI  - '):
            title = line.split('- ')[1].strip()
            # Continuar extrayendo el título si se extiende a múltiples líneas
            while True:
                next_line_index = lines.index(line) + 1
                if not lines[next_line_index].startswith('      '): break
                title += ' ' + lines[next_line_index].strip()
                line = lines[next_line_index]
            current_article['Title'] = title
        
        # Extraer Abstract
        elif line.startswith('AB  - '):
            abstract = line.split('- ')[1].strip()
            # Continuar extrayendo el abstract si se extiende a múltiples líneas
            while True:
                next_line_index = lines.index(line) + 1
                if not lines[next_line_index].startswith('      '): break
                abstract += ' ' + lines[next_line_index].strip()
                line = lines[next_line_index]
            current_article['Abstract'] = abstract

        # Extraer revista
        elif line.startswith('JT  - '):
            current_article['Journal'] = line.split('- ')[1].strip()

        # Guardar y reiniciar para el próximo artículo al encontrar una línea vacía
        if line == '':
            if current_article:
                # Asegurarse de que todos los campos requeridos están presentes
                if all(key in current_article for key in ['PMID', 'DOI', 'Title', 'Abstract', 'Journal']):
                    contenido_pubmed.append([
                        current_article['Title'],
                        current_article['DOI'],
                        current_article['PMID'],
                        current_article['Journal'],
                        current_article['Abstract']
                    ])
                # Reiniciar el diccionario para el siguiente artículo
                current_article = {}

    return contenido_pubmed
def crea_contenido_scopus(filepath):
    """
    Procesa un archivo exportado de Scopus para extraer información de artículos, libros y conferencias.
    
    Entrada:
    - filepath: Ruta al archivo que contiene los datos de Scopus.

    Salida:
    - df: DataFrame con la información extraída de artículos, libros y conferencias.
    """
    # Leer todo el contenido del archivo
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Dividir el contenido en entradas de artículos, libros y conferencias
    entries = re.split(r'@(ARTICLE|BOOK|CONFERENCE)', content)
    
    # Preparar la lista para recolectar datos
    data = []

    # Iterar sobre cada entrada para extraer información
    for i in range(1, len(entries), 2):
        entry_type = entries[i]  # Puede ser ARTICLE, BOOK o CONFERENCE
        entry_content = entries[i+1]  # Contenido del artículo, libro o conferencia

        # Extraer campos comunes, modificando la expresión para que capture múltiples líneas y caracteres especiales dentro de las llaves
        title = re.search(r'title\s*=\s*\{(.*?)\}', entry_content, re.DOTALL)
        doi = re.search(r'doi\s*=\s*\{(.*?)\}', entry_content, re.DOTALL)
        pmid = re.search(r'PMID-\s*(\d+)', entry_content)
        journal = re.search(r'journal\s*=\s*\{(.*?)\}', entry_content, re.DOTALL)
        abstract = re.search(r'abstract\s*=\s*\{(.*?)\}', entry_content, re.DOTALL)

        # Extraer el texto de cada campo, si está presente
        title_text = title.group(1) if title else 'No Title'
        doi_text = doi.group(1) if doi else 'No DOI'
        pmid_text = pmid.group(1) if pmid else 'No PMID'
        journal_text = journal.group(1) if journal else 'No Journal'
        abstract_text = abstract.group(1) if abstract else 'No Abstract'
        
        # Añadir el tipo de entrada (ARTICLE, BOOK o CONFERENCE)
        data.append([entry_type, title_text, doi_text, pmid_text, journal_text, abstract_text])

    # Crear un DataFrame con los datos recolectados
    df = pd.DataFrame(data, columns=['Type', 'Title', 'DOI', 'PMID', 'Journal', 'Abstract'])
    
    return df
def fusionar_tablas(df1, df2):
    """
    Fusiona dos DataFrames y elimina duplicados basados en 'Title', luego restablece el índice.

    Entrada:
    - df1: DataFrame con artículos de Scopus.
    - df2: DataFrame con artículos de PubMed.

    Salida:
    - DataFrame fusionado sin duplicados y con índice restablecido.
    """
    # Concatenar ambos DataFrames
    df_fusionado = pd.concat([df1, df2], ignore_index=True)

    # Eliminar duplicados basándose en la columna 'Title'
    df_fusionado = df_fusionado.drop_duplicates(subset=['Title'])

    # Restablecer el índice para que sea continuo
    df_fusionado.reset_index(drop=True, inplace=True)

    return df_fusionado
def crea_contenido_pubmed(filepath):
    # Inicializar la lista para almacenar los datos extraídos
    contenido_pubmed = []

    # Leer el contenido del archivo
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()

    # Variables temporales para almacenar información de cada artículo
    current_article = {}

    for i, line in enumerate(lines):
        # Extraer PMID
        if line.startswith('PMID- '):
            current_article['PMID'] = line.split('- ')[1].strip()
        
        # Extraer DOI
        elif line.startswith('LID - ') and '[doi]' in line:
            current_article['DOI'] = line.split(' [doi]')[0].split('- ')[1].strip()
        
        # Extraer título del artículo
        elif line.startswith('TI  - '):
            title = line[6:].strip()
            # Continuar extrayendo el título si se extiende a múltiples líneas
            j = i + 1
            while j < len(lines) and lines[j].startswith('      '):
                title += ' ' + lines[j].strip()
                j += 1
            current_article['Title'] = title
        
        # Extraer Abstract
        elif line.startswith('AB  - '):
            abstract = line[6:].strip()
            j = i + 1
            while j < len(lines) and lines[j].startswith('      '):
                abstract += ' ' + lines[j].strip()
                j += 1
            current_article['Abstract'] = abstract

        # Extraer revista
        elif line.startswith('JT  - '):
            current_article['Journal'] = line[6:].strip()

        # Guardar y reiniciar para el próximo artículo al encontrar una línea vacía
        if line == '':
            if current_article:
                # Solo requerir que estén presentes 'PMID', 'Title' y 'Abstract'
                if all(key in current_article for key in ['PMID', 'Title', 'Abstract']):
                    contenido_pubmed.append([
                        current_article.get('Title', 'No Title'),
                        current_article.get('DOI', 'No DOI'),
                        current_article.get('PMID', 'No PMID'),
                        current_article.get('Journal', 'No Journal'),
                        current_article.get('Abstract', 'No Abstract')
                    ])
                # Reiniciar el diccionario para el siguiente artículo
                current_article = {}

    # Asegurarse de agregar el último artículo si el archivo no termina en una línea en blanco
    if current_article:
        if all(key in current_article for key in ['PMID', 'Title', 'Abstract']):
            contenido_pubmed.append([
                current_article.get('Title', 'No Title'),
                current_article.get('DOI', 'No DOI'),
                current_article.get('PMID', 'No PMID'),
                current_article.get('Journal', 'No Journal'),
                current_article.get('Abstract', 'No Abstract')
            ])

    # Convertir la lista a DataFrame
    df = pd.DataFrame(contenido_pubmed, columns=['Title', 'DOI', 'PMID', 'Journal', 'Abstract'])
    return df

    """
    Fusiona dos DataFrames y elimina duplicados basados en 'PMID', luego restablece el índice.

    Entrada:
    - df1: DataFrame con artículos de Scopus.
    - df2: DataFrame con artículos de PubMed.

    Salida:
    - DataFrame fusionado sin duplicados y con índice restablecido.
    """
    
    
    
    
    # Concatenar ambos DataFrames
    df_fusionado = pd.concat([df1, df2], ignore_index=True)

    # Eliminar duplicados basándose en la columna 'PMID'
    df_fusionado = df_fusionado.drop_duplicates(subset=['DOI'])

    # Restablecer el índice para que sea continuo
    df_fusionado.reset_index(drop=True, inplace=True)

    return df_fusionado
def ordenar_por_titulo(tabla_fusionada):
    """
    Esta función toma un DataFrame con artículos y los ordena alfabéticamente por el título,
    sin distinguir entre mayúsculas y minúsculas.

    Entrada:
    - tabla_fusionada: DataFrame con los artículos (debe tener una columna 'Title').

    Salida:
    - DataFrame ordenado alfabéticamente por el título.
    """
    # Ordenar el DataFrame por la columna 'Title' sin distinguir entre mayúsculas y minúsculas
    tabla_ordenada = tabla_fusionada.sort_values(by='Title', key=lambda x: x.str.lower(), ascending=True)
    
    # Reiniciar el índice para que sea continuo
    tabla_ordenada.reset_index(drop=True, inplace=True)
    
    return tabla_ordenada
def screaning(df, lim=None):
    resultados = []
    inicio = lim[0] - 1 if lim else 0
    fin = lim[1] if lim else len(df)

    for index, row in df.iloc[inicio:fin].iterrows():
        prompt = f"""
        Estoy realizando un screening para una revisión sistemática en el campo de cáncer, con un enfoque en la representación de datos en repositorios de investigación. El objetivo es determinar si un artículo debe ser incluido o no, basado en si menciona algún tipo de modelo basado en conocimiento como ontologías, mapas semánticos, grafos de conocimiento, metamodelos u otros tipos para ayudar en la representación de datos para por ejemplo el almacenamiento, integración y recuperación de datos heterogéneos. Otros tipos de modelos como redes neuronales son basadas en datos y no deben ser considerados, es decir que la respuesta es “No”.
        Tambien se debe excluir aquellos trabajos que son revisión sistematicas. Lee cuidadosamente el siguiente abstract y determina si debe estar incluido. Justifica tu decisión en 2 líneas máximo, proporciona una traducción fiel al español y realiza un breve resumen indicando la idea principal y la novedad del artículo.
        
        Abstract: {row['Abstract']}

        Responde en el siguiente formato:
        S1: [Incluir 'SI' o 'NO']
        S2: [Justificación de la decisión]
        S3: [Traducción del abstract al español]
        S4: [Resumen corto del artículo]
        """

        # Llamar a quest_gpt para procesar el prompt y obtener la respuesta
        respuesta_gpt = quest_gpt(prompt)

        # Extraer los datos desde la respuesta, adaptar según el formato específico que quest_gpt devuelve
        decision = respuesta_gpt.split("S1:")[1].split("\n")[0].strip()
        justificacion = respuesta_gpt.split("S2:")[1].split("\n")[0].strip()
        traduccion = respuesta_gpt.split("S3:")[1].split("\n")[0].strip()
        resumen = respuesta_gpt.split("S4:")[1].strip()

        resultados.append([traduccion, resumen, decision, justificacion])

    # Crear DataFrame de resultados
    resultados_df = pd.DataFrame(resultados, columns=['Traducción', 'Resumen', 'Inclusión', 'Justificación'])

    # Añadir resultados a la tabla original solo para el rango especificado
    df.loc[inicio:fin-1, ['Traducción', 'Resumen', 'Inclusión', 'Justificación']] = resultados_df.values

    return df
def screaning2(df, archivo_salida, inicio=1, paso=2):
    # Cargar el DataFrame existente si el archivo ya existe y el inicio es mayor que 1
    try:
        if inicio > 1:
            df = pd.read_excel(archivo_salida, index_col=None)
            print(f"Se cargó el DataFrame existente desde {archivo_salida}. Continuando desde el artículo {inicio}.")
        else:
            print("Iniciando desde el principio.")
    except FileNotFoundError:
        print("Archivo no encontrado, iniciando un nuevo proceso de evaluación.")

    total_articulos = len(df)
    
    # Procesar en bloques
    for i in range(inicio, total_articulos + 1, paso):
        fin = min(i + paso - 1, total_articulos)  # Asegurarse de no pasarse del rango
        print(f"Procesando artículos {i} a {fin}.")
        
        # Evaluar los artículos en el rango especificado
        df_actualizado = screaning(df, [i, fin])
        
        # Guardar el DataFrame en Excel
        df_actualizado.to_excel(archivo_salida, index=False)
        print(f"Datos guardados en {archivo_salida}. Progreso: Artículo {fin} de {total_articulos}.")

    print("Procesamiento completado.")
def exportar_a_excel(df, ruta_archivo):
    """
    Exporta un DataFrame a un archivo Excel.
    
    Entrada:
    - df: DataFrame que contiene los datos a exportar.
    - ruta_archivo: Ruta completa y nombre del archivo donde se guardará el Excel.
    """
    df.to_excel(ruta_archivo, index=False)
    print(f'Archivo Excel guardado en {ruta_archivo}')


ruta_archivopub = "C:\\UNAB\\CECAN\\Revision Sistematica\\pubmed.txt"
datos_pubmed = crea_contenido_pubmed(ruta_archivopub)
ruta_archivo = "C:\\UNAB\\CECAN\\Revision Sistematica\\scopus.bib"
datos_scopus = crea_contenido_scopus(ruta_archivo)
datos_fusionados = fusionar_tablas(datos_scopus, datos_pubmed)
datos_ordenados = ordenar_por_titulo(datos_fusionados)

archivo_salida = 'C:\\UNAB\\CECAN\\Revision Sistematica\\salida.xlsx'
screaning2(datos_ordenados, archivo_salida, inicio=8)



# Mostrar el resultado
print(datos_ordenados.head())






ruta_archivo = "C:\\UNAB\\LLM\\Pubmed_export\\pubmedcancer.txt"
datos_pubmed = crea_contenido_pubmedfile(ruta_archivo)






datos = pmc_to_datos_pubmed2(datos_pubmed)



# Ejemplo de uso de la clase Coleccion
mi_coleccion = Coleccion("C:\\UNAB\\LLM\\Pubmed", "Colección de artículos de investigación")
#extraer_contenido_total(mi_coleccion)
extraer_contenido_total_porlinea(mi_coleccion)
extrae_capitulos_tamaño(mi_coleccion)


#extraer_capitulos_patron3(mi_coleccion)


ruta_archivo = "C:\\UNAB\\LLM\\Pubmed_export\\pubmedcancer.txt"
datos_pubmed = crea_contenido_pubmedfile(ruta_archivo)
for dato in datos_pubmed:
    print(dato)






ruta_archivo = "C:\\UNAB\\LLM\\Pubmed_export\\pubmedcancer.txt"
datos_pubmed = crea_contenido_pubmedfile(ruta_archivo)
for dato in datos_pubmed:
    print(dato)







#extraer_capitulos_patron2(mi_coleccion)






separar_por_lineas(mi_coleccion)


extraer_capitulos_patron(mi_coleccion)


#extraer_capitulos_gpt(mi_coleccion)

# Ejemplo de cómo usar la función:
# Asumiendo que 'mi_coleccion' es una instancia de la clase Coleccion que ya contiene textos en 'contenido'
#separar_frases(mi_coleccion)
# print(mi_coleccion.separa_frases)  # Para verificar la estructura de frases
# print(mi_coleccion.tabla_historia)  # Para ver el historial actualizado


# Mostrar información sobre la colección
print(mi_coleccion.contenido[1])
print("Número de PDFs:", mi_coleccion.n)
print("Ubicación de la colección:", mi_coleccion.ubicacion)
print("Descripción de la colección:", mi_coleccion.descripcion)
print("Títulos en la colección:", mi_coleccion.elementos)
print("Historial de la colección:", mi_coleccion.tabla_historia)
