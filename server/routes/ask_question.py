from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional

from modules.llm import get_llm_chain
from modules.query_handlers import query_chain
from modules.load_vectorstore import get_pinecone_index

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from logger import logger

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(request: QuestionRequest):
    try:
        question = request.question
        logger.info(f"User query: {question}")

        index = get_pinecone_index()

        embed_model = GoogleGenerativeAIEmbeddings(
            model="gemini-embedding-001",
            output_dimensionality=768,
        )

        embedded_query = embed_model.embed_query(question)

        
        res = index.query(
            vector=embedded_query,
            top_k=3,
            include_metadata=True
        )

        
        if not res.get("matches"):
            return {
                "answer": "⚠️ No relevant documents found. Please upload PDFs first."
            }

       
        docs = [
            Document(
                page_content=match["metadata"].get("text", ""),
                metadata=match["metadata"]
            )
            for match in res["matches"]
        ]

       
        class SimpleRetriever(BaseRetriever):
            tags: Optional[List[str]] = Field(default_factory=list)
            metadata: Optional[dict] = Field(default_factory=dict)

            def __init__(self, documents: List[Document]):
                super().__init__()
                self._docs = documents

            def _get_relevant_documents(self, query: str) -> List[Document]:
                return self._docs

        retriever = SimpleRetriever(docs)

        chain = get_llm_chain(retriever)

        result = query_chain(chain, question)

        logger.info("Query successful")

        return result

    except Exception as e:
        logger.exception("Error processing question")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )