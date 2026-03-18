def chunk_text(text, size=350):

    words = text.split()
    chunks = []

    for i in range(0, len(words), size):
        chunks.append(" ".join(words[i:i+size]))

    return chunks