import os
from pathlib import Path
import time
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()
BATCH_SIZE = 80      # under the 100/min limit
PAUSE_SECONDS = 65   # wait a bit over a minute

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")

# not used yet, we need it when we build the agent
llm = ChatGoogleGenerativeAI(
    model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


def chunker(file):
    """Read one .txt file and split it into chunks."""
    with open(file, encoding="utf-8") as f:
        text = f.read()
    return splitter.create_documents([text], metadatas=[{"source": str(file)}])


def pdf_chunker(file):
    """Read one PDF page by page and split each page into chunks."""
    reader = PdfReader(file)
    chunks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text or not text.strip():
            continue  # skip empty or scanned pages
        page_chunks = splitter.create_documents(
            [text], metadatas=[{"source": str(file), "page": i + 1}]
        )
        for chunk in page_chunks:
            if "......" in chunk.page_content:
                continue  # skip table-of-contents lines
            chunks.append(chunk)
    return chunks

def build_store(folder="docs"):
    """Load every .txt and .pdf in the folder and build the search index."""
    all_chunks = []
    for path in Path(folder).glob("*.txt"):
        all_chunks.extend(chunker(path))
    for path in Path(folder).glob("*.pdf"):
        all_chunks.extend(pdf_chunker(path))

    if not all_chunks:
        raise ValueError(f"No text found in '{folder}'. Add .txt or .pdf files.")

    print(f"Loaded {len(all_chunks)} chunks")
    store = InMemoryVectorStore(embeddings)
    store.add_documents(all_chunks)
    return store


def search_notes(store, question, k=5):
    """Return the k most relevant chunks as text, with their sources."""
    results = store.similarity_search(question, k=k)
    parts = []
    for doc in results:
        name = Path(doc.metadata["source"]).name
        page = doc.metadata.get("page")
        label = f"{name}, page {page}" if page else name
        parts.append(f"[{label}]\n{doc.page_content}")
    return "\n\n".join(parts)

def get_store(folder="docs", cache="store.json"):
    """Load the saved index if it exists, otherwise build it and save it."""
    if Path(cache).exists():
        return InMemoryVectorStore.load(cache, embeddings)
    store = build_store(folder)
    store.dump(cache)
    return store

if __name__ == "__main__":
    store = get_store()
    print(search_notes(store, "why does 5G signal drop indoors?"))