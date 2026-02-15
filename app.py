import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Tuple

import resend
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
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

# In-memory OTP storage: {email: (otp_code, timestamp)}
otp_storage: Dict[str, Tuple[str, datetime]] = {}

# OTP Configuration
OTP_EXPIRY_MINUTES = 5
OTP_LENGTH = 6


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str


class SendOTPRequest(BaseModel):
    email: EmailStr


class SendOTPResponse(BaseModel):
    message: str
    email: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str


class VerifyOTPResponse(BaseModel):
    message: str
    verified: bool


def load_profile_text() -> str:
    if not INFO_PATH.exists():
        raise FileNotFoundError("information.txt not found")
    return INFO_PATH.read_text(encoding="utf-8").strip()


def get_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not set")
    return Groq(api_key=api_key)


def generate_otp() -> str:
    """Generate a random 6-digit OTP."""
    return ''.join([str(random.randint(0, 9)) for _ in range(OTP_LENGTH)])


def send_email_otp(email: str, otp: str) -> None:
    """Send OTP via email using Resend API."""
    resend_api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "Auth <auth@mukesh.tech>")
    
    if not resend_api_key:
        raise RuntimeError("RESEND_API_KEY must be set in environment variables")
    
    # Set Resend API key
    resend.api_key = resend_api_key
    
    # Create HTML email body
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h2 style="color: #333; margin-bottom: 20px;">AI Chat Verification</h2>
                <p style="color: #666; font-size: 16px; margin-bottom: 20px;">Your One-Time Password (OTP) for accessing the AI chat is:</p>
                <div style="background-color: #f0f9ff; padding: 20px; border-radius: 8px; text-align: center; margin: 30px 0;">
                    <h1 style="color: #4CAF50; letter-spacing: 8px; font-size: 36px; margin: 0;">{otp}</h1>
                </div>
                <p style="color: #666; font-size: 14px; margin-bottom: 10px;">This OTP is valid for <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.</p>
                <p style="color: #999; font-size: 12px; margin-top: 30px; border-top: 1px solid #eee; padding-top: 20px;">If you didn't request this OTP, please ignore this email.</p>
            </div>
        </body>
    </html>
    """
    
    # Send email via Resend
    try:
        params: resend.Emails.SendParams = {
            "from": from_email,
            "to": [email],
            "subject": "Your OTP for AI Chat Access",
            "html": html_body,
        }
        resend.Emails.send(params)
    except Exception as exc:
        raise RuntimeError(f"Failed to send email via Resend: {exc}") from exc


def clean_expired_otps() -> None:
    """Remove expired OTPs from storage."""
    current_time = datetime.now()
    expired_emails = [
        email for email, (_, timestamp) in otp_storage.items()
        if current_time - timestamp > timedelta(minutes=OTP_EXPIRY_MINUTES)
    ]
    for email in expired_emails:
        del otp_storage[email]


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/send-otp", response_model=SendOTPResponse)
def send_otp(payload: SendOTPRequest) -> SendOTPResponse:
    """Send OTP to the provided email address."""
    email = payload.email.lower()
    
    # Clean expired OTPs
    clean_expired_otps()
    
    # Generate new OTP
    otp = generate_otp()
    
    # Send email
    try:
        send_email_otp(email, otp)
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    
    # Store OTP with timestamp
    otp_storage[email] = (otp, datetime.now())
    
    return SendOTPResponse(
        message=f"OTP has been sent to {email}",
        email=email
    )


@app.post("/verify-otp", response_model=VerifyOTPResponse)
def verify_otp(payload: VerifyOTPRequest) -> VerifyOTPResponse:
    """Verify the OTP provided by the user."""
    email = payload.email.lower()
    otp = payload.otp.strip()
    
    # Clean expired OTPs
    clean_expired_otps()
    
    # Check if OTP exists for this email
    if email not in otp_storage:
        raise HTTPException(
            status_code=400, 
            detail="No OTP found for this email or OTP has expired"
        )
    
    stored_otp, timestamp = otp_storage[email]
    
    # Check if OTP has expired
    if datetime.now() - timestamp > timedelta(minutes=OTP_EXPIRY_MINUTES):
        del otp_storage[email]
        raise HTTPException(
            status_code=400,
            detail="OTP has expired. Please request a new one"
        )
    
    # Verify OTP
    if stored_otp != otp:
        raise HTTPException(
            status_code=400,
            detail="Invalid OTP. Please try again"
        )
    
    # OTP is valid - remove it from storage
    del otp_storage[email]
    
    return VerifyOTPResponse(
        message="Email verified successfully",
        verified=True
    )


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
        "You are a friendly portfolio assistant helping visitors learn about me. "
        "Use the provided profile information to answer questions about my background, skills, experience, and projects. "
        "Be conversational and engaging when responding. "
        "If someone asks about something unrelated to my profile (like general topics, current events, or other people), "
        "politely redirect them by saying something like 'I'm here to talk about my background and experience. "
        "Feel free to ask me about my skills, projects, or professional journey!' "
        "Stay focused on helping people get to know me through the information provided."
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
