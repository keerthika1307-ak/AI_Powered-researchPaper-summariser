import fitz  # PyMuPDF

def extract_text_from_pdf(uploaded_file) -> str:
    # uploaded_file is a Streamlit UploadedFile (has .read())
    data = uploaded_file.read()
    doc = fitz.open(stream=data, filetype='pdf')
    texts = []
    for page in doc:
        try:
            texts.append(page.get_text())
        except Exception:
            texts.append('')
    return '\n'.join(texts)