import fitz  # PyMuPDF

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
                    if block.get("type", 0) == 0 and "lines" in block:  # type 0 indica un bloque de texto
                        for line in block["lines"]:
                            for span in line["spans"]:  # Itera sobre fragmentos (spans)
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

    except (FileNotFoundError, ValueError) as e:
        print(f"Error al procesar el PDF: {e}")
        return None
