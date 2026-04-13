import os
import time
from pathlib import Path
from dotenv import load_dotenv
from tqdm.auto import tqdm
from pinecone import Pinecone, ServerlessSpec
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_ENV = "us-east-1"
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "medicalindex")

if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

UPLOAD_DIR = "./uploaded_docs"

if os.path.exists(UPLOAD_DIR):
    if not os.path.isdir(UPLOAD_DIR):
        os.remove(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR)
else:
    os.makedirs(UPLOAD_DIR)


_pc = None
_index = None


def get_pinecone_index():
    """Lazily connect to Pinecone so startup doesn't crash."""
    global _pc, _index

    if _index is not None:
        return _index

    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise RuntimeError("PINECONE_API_KEY is not set. Add it to Railway variables.")

    _pc = Pinecone(api_key=api_key)

    spec = ServerlessSpec(cloud="aws", region=PINECONE_ENV)

    existing_indexes = [i["name"] for i in _pc.list_indexes()]

    if PINECONE_INDEX_NAME not in existing_indexes:
        _pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=768,
            metric="dotproduct",
            spec=spec,
        )

        while not _pc.describe_index(PINECONE_INDEX_NAME).status["ready"]:
            time.sleep(1)

    _index = _pc.Index(PINECONE_INDEX_NAME)
    return _index


def load_vectorstore(uploaded_files):
    index = get_pinecone_index()

    embed_model = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",
        output_dimensionality=768,
    )

    file_paths = []

    # 1. upload
    for file in uploaded_files:
        save_path = Path(UPLOAD_DIR) / file.filename
        with open(save_path, "wb") as f:
            f.write(file.file.read())
        file_paths.append(str(save_path))

    # 2. split
    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100
        )
        chunks = splitter.split_documents(documents)

        texts = [chunk.page_content for chunk in chunks]
        metadata = [chunk.metadata for chunk in chunks]
        ids = [f"{Path(file_path).stem}-{i}" for i in range(len(chunks))]

        # 3. embedding
        print("Embedding chunks...")
        embeddings = embed_model.embed_documents(texts)

        # 4. upsert
        print("Upserting embeddings...")

        with tqdm(total=len(embeddings), desc="Upserting to Pinecone") as progress:
            index.upsert(vectors=list(zip(ids, embeddings, metadata)))
            progress.update(len(embeddings))

        print(f"Upload complete for {file_path}")