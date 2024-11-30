import os
import glob
import re
import pandas as pd

def sanitizar_nombre_archivo(nombre):
    # Reemplazar caracteres no permitidos por guiones bajos
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', nombre)

def crear_archivo_excel(ruta_carpeta, ruta_excel):
    # Verificar si la ruta de la carpeta existe
    if not os.path.exists(ruta_carpeta):
        raise FileNotFoundError("Error: La ruta de la carpeta no existe.")

    # Obtener todos los archivos PDF en la carpeta indicada
    archivos_pdf = glob.glob(os.path.join(ruta_carpeta, "*.pdf"))

    # Verificar si se encontraron archivos PDF
    if not archivos_pdf:
        raise FileNotFoundError("Error: No se encontraron archivos PDF en la carpeta especificada.")

    # Crear un DataFrame con los nombres originales y una columna vacía para los nuevos nombres
    data = {
        'Nombre Original': [os.path.basename(archivo) for archivo in archivos_pdf],  # Extraer solo el nombre del archivo sin la ruta
        'Nombre Nuevo': ['' for _ in archivos_pdf]  # Columna vacía para los nuevos nombres
    }
    df = pd.DataFrame(data)

    # Guardar el DataFrame en un archivo Excel
    df.to_excel(ruta_excel, index=False)
    print(f"Archivo Excel creado: {ruta_excel}")

def renombrar_archivos_pdf(ruta_carpeta, ruta_excel, sanitizar=True):
    # Verificar si la ruta de la carpeta existe
    if not os.path.exists(ruta_carpeta):
        raise FileNotFoundError("Error: La ruta de la carpeta no existe.")

    # Leer el archivo Excel
    df = pd.read_excel(ruta_excel)

    # Verificar si el Excel tiene las columnas necesarias
    if 'Nombre Original' not in df.columns or 'Nombre Nuevo' not in df.columns:
        raise ValueError("Error: El archivo Excel debe tener las columnas 'Nombre Original' y 'Nombre Nuevo'.")

    # Obtener todos los archivos PDF en la carpeta indicada
    archivos_pdf = set(glob.glob(os.path.join(ruta_carpeta, "*.pdf")))

    # Verificar si se encontraron archivos PDF
    if not archivos_pdf:
        raise FileNotFoundError("Error: No se encontraron archivos PDF en la carpeta especificada.")

    # Lista para almacenar los nombres originales, nuevos y el resultado de la operación
    nombres_originales = []

    # Renombrar cada archivo con el nombre del Excel
    for _, row in df.iterrows():
        nombre_original = row['Nombre Original']
        nombre_nuevo = row['Nombre Nuevo'].strip()
        # Sanitizar el nuevo nombre del archivo si la opción está habilitada
        if sanitizar:
            nombre_nuevo = sanitizar_nombre_archivo(nombre_nuevo)
        ruta_original = os.path.join(ruta_carpeta, nombre_original)  # Ruta completa del archivo original
        ruta_nueva = os.path.join(ruta_carpeta, f"{nombre_nuevo}.pdf")  # Ruta completa con el nuevo nombre
        try:
            # Verificar si el archivo original existe en la lista de archivos
            if ruta_original in archivos_pdf:
                os.rename(ruta_original, ruta_nueva)  # Renombrar el archivo
                nombres_originales.append((ruta_original, ruta_nueva, "Éxito"))  # Registrar éxito
                print(f"Archivo renombrado: {ruta_original} -> {ruta_nueva}")
            else:
                nombres_originales.append((ruta_original, ruta_nueva, "Error: No se encontró el archivo"))  # Registrar error
                print(f"Error: No se encontró el archivo {ruta_original} en la carpeta especificada.")
        except Exception as e:
            # Registrar el error si ocurre durante el renombrado
            nombres_originales.append((ruta_original, ruta_nueva, f"Error: {e}"))
            print(f"Error al renombrar el archivo {ruta_original}: {e}")

    # Guardar los nombres originales, nuevos y el resultado de la operación en un archivo de texto
    with open(os.path.join(ruta_carpeta, "nombres_originales.txt"), "w") as archivo:
        for original, nuevo, resultado in nombres_originales:
            archivo.write(f"{original} -> {nuevo} : {resultado}\n")  # Escribir el resultado de cada operación

# Ejemplo de uso
ruta_carpeta = "ruta/a/tu/carpeta"
ruta_excel = "ruta/a/tu/archivo.xlsx"
crear_archivo_excel(ruta_carpeta, ruta_excel)
renombrar_archivos_pdf(ruta_carpeta, ruta_excel, sanitizar=True)
