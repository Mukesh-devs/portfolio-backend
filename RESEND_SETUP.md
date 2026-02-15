# Resend API Configuration for OTP Emails

## ✅ What Changed

Your OTP system now uses **Resend** instead of traditional SMTP:
- ✉️ **No more Gmail App Passwords or SMTP configuration**
- 🚀 **Modern email API** - faster and more reliable
- 🎨 **Enhanced email template** with better styling
- 🔧 **Simpler setup** - just one API key needed

---

## 🔑 Setup Instructions

### 1. Add your Resend API key to `.env`

Create or update your `.env` file:

```env
# Groq API Configuration
GROQ_API_KEY=your_groq_api_key_here

# Resend API Configuration
RESEND_API_KEY=re_9mWcApMQ_PRkqvctX65J6hw9satfUtPg7
FROM_EMAIL=Auth <auth@mukesh.tech>
```

**Note:** I've included your Resend API key from `resend_verify.py`. Make sure your domain (`mukesh.tech`) is verified in the Resend dashboard.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the server

```bash
uvicorn app:app --reload --port 8000
```

---

## 🧪 Test the OTP System

### Test 1: Send OTP
```bash
curl -X POST http://localhost:8000/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "testinginmyplatform@gmail.com"}'
```

**Expected Response:**
```json
{
  "message": "OTP has been sent to testinginmyplatform@gmail.com",
  "email": "testinginmyplatform@gmail.com"
}
```

### Test 2: Verify OTP
Check your email for the 6-digit code, then:

```bash
curl -X POST http://localhost:8000/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email": "testinginmyplatform@gmail.com", "otp": "123456"}'
```

**Expected Response:**
```json
{
  "message": "Email verified successfully",
  "verified": true
}
```

---

## 📧 Email Template

The OTP email now features:
- Professional layout with centered design
- Large, easy-to-read OTP display
- Color-coded styling (`#4CAF50` green)
- Clear expiry information
- Responsive design that looks good on all devices

---

## 🔐 Resend Dashboard

Manage your email sending at: [https://resend.com/dashboard](https://resend.com/dashboard)

**Features:**
- View email logs and delivery status
- Monitor bounce rates
- Add/verify domains
- Generate API keys
- Set up webhooks for email events

---

## 🛠 API Endpoints (Unchanged)

Your OTP endpoints work exactly the same:

### 1. `POST /send-otp`
Request:
```json
{
  "email": "user@example.com"
}
```

### 2. `POST /verify-otp`
Request:
```json
{
  "email": "user@example.com",
  "otp": "123456"
}
```

### 3. `POST /ask` (AI Chat - after verification)
Request:
```json
{
  "question": "What is your experience?"
}
```

---

## 🌐 Frontend Integration (No Changes Needed)

Your frontend code remains the same! The API interface hasn't changed:

```javascript
// 1. Send OTP
const response = await fetch('http://localhost:8000/send-otp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: userEmail })
});

// 2. Verify OTP
const verifyResponse = await fetch('http://localhost:8000/verify-otp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ email: userEmail, otp: userOtp })
});

// 3. Use AI Chat
const chatResponse = await fetch('http://localhost:8000/ask', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ question: userQuestion })
});
```

---

## 📊 Benefits of Resend over SMTP

| Feature | SMTP (Gmail) | Resend |
|---------|--------------|--------|
| Setup Complexity | High | Low |
| API Key | App Password | Simple API key |
| Email Limits | Restrictive | Generous free tier |
| Deliverability | Variable | Optimized |
| Analytics | None | Built-in dashboard |
| Custom Domain | Difficult | Easy |
| Developer Experience | Complex | Modern & simple |

---

## 🚨 Troubleshooting

### Issue: "RESEND_API_KEY must be set"
**Solution:** Make sure `.env` file exists and contains `RESEND_API_KEY=re_...`

### Issue: Email not delivered
**Solutions:**
1. Check Resend dashboard for delivery status
2. Verify your domain is confirmed in Resend
3. Check spam folder
4. Ensure FROM_EMAIL uses your verified domain

### Issue: "Domain not verified"
**Solution:** 
1. Go to [Resend Dashboard](https://resend.com/domains)
2. Add your domain (`mukesh.tech`)
3. Add DNS records as instructed
4. Wait for verification (can take up to 72 hours)

---

## 🔄 Switching Back to SMTP (if needed)

If you need to use SMTP instead:
1. Restore the old `send_email_otp` function from git history
2. Update `.env` with SMTP credentials
3. Change imports back to include `smtplib`, `MIMEText`, etc.

---

## 📝 Production Checklist

Before deploying:
- [ ] Add `.env` to `.gitignore`
- [ ] Use environment variables in production (not `.env` file)
- [ ] Verify domain in Resend dashboard
- [ ] Test email delivery to multiple providers (Gmail, Outlook, etc.)
- [ ] Set up rate limiting on `/send-otp` endpoint
- [ ] Monitor email delivery in Resend dashboard
- [ ] Consider implementing session tokens after OTP verification

---

## 💡 Next Steps

Consider these enhancements:
1. **Rate Limiting:** Prevent OTP spam
   ```bash
   pip install slowapi
   ```

2. **Redis Storage:** Replace in-memory OTP storage
   ```bash
   pip install redis
   ```

3. **Session Tokens:** Issue JWT after OTP verification
   ```bash
   pip install pyjwt
   ```

4. **Email Templates:** Create reusable HTML templates
5. **Webhook Integration:** Track email opens and clicks

---

Your OTP system is now configured with Resend! 🎉
