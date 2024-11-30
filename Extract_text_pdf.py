import fitz  # PyMuPDF
import json

def extract_text_with_details(pdf_path):
    """
    Extrae líneas de texto de un archivo PDF junto con sus detalles como tipo de fuente y tamaño, 
    procesando solo los bloques que contengan texto.

    Args:
        pdf_path (str): Ruta al archivo PDF.

    Returns:
        list: Lista de detalles de texto (líneas, fuente, tamaño, posición).
    """
    try:
        text_details = []
        char_count = 0  # Contador de caracteres incremental

        # Abre el documento PDF con un contexto
        with fitz.open(pdf_path) as pdf_document:
            # Itera sobre todas las páginas
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text_dict = page.get_text("dict")  # Obtiene el texto estructurado como diccionario
                
                for block in text_dict.get("blocks", []):
                    # Procesa solo los bloques que contengan texto y no imágenes u otros elementos
                    if block.get("type", 0) == 0:
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):  # Itera sobre fragmentos (spans)
                                char_count += len(span["text"])  # Incrementa el contador de caracteres
                                detail = {
                                    "page": page_num + 1,
                                    "block_bbox": block["bbox"],  # Posición del bloque
                                    "line_bbox": line["bbox"],    # Posición de la línea
                                    "text": span["text"],         # Texto del span
                                    "font": span["font"],         # Tipo de fuente
                                    "size": span["size"],         # Tamaño de la fuente
                                    "color": span["color"],       # Color del texto
                                    "char_count": char_count       # Contador de caracteres acumulado
                                }
                                text_details.append(detail)

        return text_details

    except (FileNotFoundError, ValueError, TypeError) as e:
        print(f"Error al procesar el PDF: {e}")
        return None


def extract_text_with_details_block(pdf_path):
    """
    Extrae líneas de texto de un archivo PDF junto con sus detalles como tipo de fuente y tamaño, 
    procesando solo los bloques que contengan texto.

    Args:
        pdf_path (str): Ruta al archivo PDF.

    Returns:
        list: Lista de detalles de texto (líneas, fuente, tamaño, posición).
    """
    try:
        text_details = []
        char_count = 0  # Contador de caracteres incremental

        # Abre el documento PDF con un contexto
        with fitz.open(pdf_path) as pdf_document:
            # Itera sobre todas las páginas
            for page_num in range(pdf_document.page_count):
                page = pdf_document.load_page(page_num)
                text_blocks = page.get_text("blocks")  # Obtiene el texto estructurado como bloques
                
                for block in text_blocks:
                    # Procesa solo los bloques que contengan texto y no imágenes u otros elementos
                    if block[4] != "":
                        detail = {
                            "page": page_num + 1,
                            "block_bbox": block[1],  # Posición del bloque
                            "text": block[4],         # Texto del bloque
                            "char_count": char_count + len(block[4])  # Contador de caracteres acumulado
                        }
                        char_count += len(block[4])
                        text_details.append(detail)

        return text_details

    except (FileNotFoundError, ValueError, TypeError) as e:
        print(f"Error al procesar el PDF: {e}")
        return None


def save_text_details_to_json(text_details, output_path):
    """
    Guarda la lista de detalles de texto en un archivo JSON.

    Args:
        text_details (list): Lista de detalles de texto.
        output_path (str): Ruta para guardar el archivo JSON.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(text_details, json_file, ensure_ascii=False, indent=4)
    except (OSError, TypeError) as e:
        print(f"Error al guardar el archivo JSON: {e}")

# Ejemplo de uso
def main():
    pdf_path = "ruta/al/archivo.pdf"
    output_json_path = "ruta/al/archivo.json"

    text_details = extract_text_with_details(pdf_path)
    if text_details:
        save_text_details_to_json(text_details, output_json_path)

if __name__ == "__main__":
    main()
