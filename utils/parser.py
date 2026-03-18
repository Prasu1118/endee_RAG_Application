import PyPDF2

def parse_file(file):

    if file.filename.endswith(".pdf"):
        reader = PyPDF2.PdfReader(file)
        text = ""

        for p in reader.pages:
            text += p.extract_text() + "\n"

        return text

    return file.read().decode("utf-8")