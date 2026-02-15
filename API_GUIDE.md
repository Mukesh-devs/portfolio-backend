# OTP Email Verification API Guide

## Overview
This API provides email-based OTP (One-Time Password) verification before users can access the AI chat functionality.

## Authentication Flow

1. **User enters email** → Frontend calls `/send-otp`
2. **User receives OTP via email** (6-digit code, valid for 5 minutes)
3. **User enters OTP** → Frontend calls `/verify-otp`
4. **If verified** → User can access the `/ask` chat endpoint

---

## API Endpoints

### 1. Send OTP
**Endpoint:** `POST /send-otp`

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Success Response (200):**
```json
{
  "message": "OTP has been sent to user@example.com",
  "email": "user@example.com"
}
```

**Error Responses:**
- `400` - Invalid email format
- `500` - Email sending failed (check SMTP configuration)

---

### 2. Verify OTP
**Endpoint:** `POST /verify-otp`

**Request Body:**
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

**Success Response (200):**
```json
{
  "message": "Email verified successfully",
  "verified": true
}
```

**Error Responses:**
- `400` - Invalid email format
- `400` - "No OTP found for this email or OTP has expired"
- `400` - "OTP has expired. Please request a new one"
- `400` - "Invalid OTP. Please try again"

---

### 3. AI Chat (Existing Endpoint)
**Endpoint:** `POST /ask`

**Note:** Call this only after successful OTP verification

**Request Body:**
```json
{
  "question": "What is your experience?"
}
```

**Success Response (200):**
```json
{
  "answer": "Based on the profile information..."
}
```

---

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file based on `.env.example`:

```env
GROQ_API_KEY=your_groq_api_key_here

# For Gmail SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
FROM_EMAIL=your_email@gmail.com
```

### 3. Gmail App Password Setup
1. Go to Google Account → Security
2. Enable 2-Factor Authentication
3. Go to "App passwords"
4. Generate a new app password for "Mail"
5. Use this password as `SMTP_PASSWORD`

### 4. Run the Server
```bash
uvicorn app:app --reload --port 8000
```

---

## Frontend Integration Example

```javascript
// Step 1: Send OTP
async function sendOTP(email) {
  const response = await fetch('http://localhost:8000/send-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  
  if (!response.ok) {
    throw new Error('Failed to send OTP');
  }
  
  return await response.json();
}

// Step 2: Verify OTP
async function verifyOTP(email, otp) {
  const response = await fetch('http://localhost:8000/verify-otp', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, otp })
  });
  
  if (!response.ok) {
    throw new Error('Invalid OTP');
  }
  
  return await response.json();
}

// Step 3: Use AI Chat (after verification)
async function askQuestion(question) {
  const response = await fetch('http://localhost:8000/ask', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question })
  });
  
  return await response.json();
}

// Usage Flow
async function handleUserFlow() {
  try {
    // 1. User enters email
    const email = 'user@example.com';
    await sendOTP(email);
    alert('OTP sent! Check your email.');
    
    // 2. User enters OTP
    const otp = prompt('Enter the OTP:');
    const result = await verifyOTP(email, otp);
    
    if (result.verified) {
      // 3. User can now use chat
      const answer = await askQuestion('Tell me about yourself');
      console.log(answer);
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
```

---

## OTP Configuration

- **OTP Length:** 6 digits
- **Expiry Time:** 5 minutes
- **Storage:** In-memory (resets on server restart)
- **Security:** OTPs are removed after successful verification

---

## Testing the API

### Using cURL

```bash
# 1. Send OTP
curl -X POST http://localhost:8000/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'

# 2. Verify OTP
curl -X POST http://localhost:8000/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "otp": "123456"}'

# 3. Ask Question
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is your experience?"}'
```

---

## Security Considerations

1. **HTTPS:** Use HTTPS in production to encrypt email/OTP transmission
2. **Rate Limiting:** Consider adding rate limiting to prevent OTP spam
3. **Session Management:** For production, implement proper session tokens after OTP verification
4. **Storage:** Use Redis or database instead of in-memory storage for scalability
5. **Email Validation:** The API validates email format using Pydantic's EmailStr

---

## Production Recommendations

1. **Use Redis for OTP Storage:**
   ```python
   import redis
   r = redis.Redis(host='localhost', port=6379, db=0)
   r.setex(f"otp:{email}", 300, otp)  # 5 minutes expiry
   ```

2. **Add Rate Limiting:**
   ```python
   from slowapi import Limiter
   limiter = Limiter(key_func=get_remote_address)
   
   @app.post("/send-otp")
   @limiter.limit("3/minute")
   async def send_otp(...):
       ...
   ```

3. **Session Tokens:** After OTP verification, issue a JWT token for subsequent chat requests

4. **Logging:** Add proper logging for security audits

---

## Troubleshooting

**Issue:** Email not sending
- Check SMTP credentials in `.env`
- Verify Gmail App Password is used (not regular password)
- Check firewall/network allows SMTP port 587

**Issue:** "SMTP_USER and SMTP_PASSWORD must be set"
- Ensure `.env` file exists
- Verify environment variables are loaded

**Issue:** OTP expired
- OTPs expire after 5 minutes
- Request a new OTP using `/send-otp`
