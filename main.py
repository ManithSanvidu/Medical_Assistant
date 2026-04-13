from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Medical Assistant API is running"}

@app.get("/test")
def test():
    return {"status": "working"}

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(request: ChatRequest):
    user_message = request.message

    response = f"You said: {user_message}"

    return {
        "response": response
    }