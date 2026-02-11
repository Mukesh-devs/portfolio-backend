import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv

app = FastAPI(title="Portfolio Q&A API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

INFO_PATH = Path(__file__).with_name("information.txt")


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


def load_profile_text() -> str:
    if not INFO_PATH.exists():
        raise FileNotFoundError("information.txt not found")
    return INFO_PATH.read_text(encoding="utf-8").strip()


def get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")
    return Groq(api_key=api_key)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest) -> AskResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    try:
        profile_text = load_profile_text()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    try:
        client = get_client()
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    system_prompt = (
        "You are a portfolio assistant. Answer only using the provided profile text. "
        "If the answer is not in the profile text, say you don't have that information."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Profile:\n{profile_text}\n\nQuestion: {question}"},
    ]

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.2,
            max_tokens=512,
            top_p=1,
            stream=False,
        )
    except Exception as exc:  # noqa: BLE001 - return a safe error to client
        raise HTTPException(status_code=502, detail=f"Groq API error: {exc}") from exc

    answer = completion.choices[0].message.content.strip()
    return AskResponse(answer=answer)
