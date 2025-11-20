# 📧 Email Configuration Setup Guide

## Issues Found:

1. ❌ **Missing Environment Variables** - MAIL_USERNAME and MAIL_PASSWORD not configured
2. ❌ **Gmail Security** - Regular passwords don't work with Gmail SMTP
3. ❌ **No Error Handling** - Email failures weren't properly handled

## ✅ Fixed:

1. ✅ Added proper email configuration with fallbacks
2. ✅ Improved error handling and user feedback
3. ✅ Better email template with emojis and formatting
4. ✅ Graceful degradation when email is not configured

---

## 🚀 Setup Instructions

### Option 1: Gmail (Recommended)

#### Step 1: Enable 2-Factor Authentication
1. Go to your Google Account: https://myaccount.google.com/security
2. Enable "2-Step Verification"

#### Step 2: Generate App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" as the app
3. Select "Windows Computer" as the device
4. Click "Generate"
5. Copy the 16-character password (format: xxxx xxxx xxxx xxxx)

#### Step 3: Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:MAIL_USERNAME="your-email@gmail.com"
$env:MAIL_PASSWORD="your-app-password-here"
```

**Windows (Command Prompt):**
```cmd
set MAIL_USERNAME=your-email@gmail.com
set MAIL_PASSWORD=your-app-password-here
```

**Permanent Setup (Windows):**
1. Search "Environment Variables" in Windows
2. Click "Edit the system environment variables"
3. Click "Environment Variables" button
4. Under "User variables", click "New"
5. Add:
   - Variable name: `MAIL_USERNAME`
   - Variable value: `your-email@gmail.com`
6. Click "New" again and add:
   - Variable name: `MAIL_PASSWORD`
   - Variable value: `your-16-char-app-password`
7. Click OK and restart your terminal

---

### Option 2: Other Email Providers

#### For Outlook/Hotmail:
```powershell
$env:MAIL_SERVER="smtp-mail.outlook.com"
$env:MAIL_PORT="587"
$env:MAIL_USERNAME="your-email@outlook.com"
$env:MAIL_PASSWORD="your-password"
```

#### For Yahoo:
```powershell
$env:MAIL_SERVER="smtp.mail.yahoo.com"
$env:MAIL_PORT="587"
$env:MAIL_USERNAME="your-email@yahoo.com"
$env:MAIL_PASSWORD="your-app-password"
```

---

## 🧪 Testing Email Configuration

### Method 1: Quick Test Script

Create a file `test_email.py`:

```python
import os
from app import app, mail
from flask_mail import Message

with app.app_context():
    if app.config['MAIL_USERNAME'] and app.config['MAIL_PASSWORD']:
        try:
            msg = Message(
                subject='🧪 WARRN Email Test',
                sender=app.config['MAIL_USERNAME'],
                recipients=[app.config['MAIL_USERNAME']]  # Send to yourself
            )
            msg.body = "If you receive this, email configuration is working! ✅"
            mail.send(msg)
            print("✅ Email sent successfully!")
        except Exception as e:
            print(f"❌ Email failed: {e}")
    else:
        print("❌ MAIL_USERNAME or MAIL_PASSWORD not configured")
```

Run it:
```bash
venv\Scripts\python.exe test_email.py
```

### Method 2: Test via Application
1. Set up environment variables
2. Run the app: `py app.py`
3. Register a user with a valid email address
4. Submit a report
5. Check if email is received

---

## 🔧 Troubleshooting

### Error: "Username and Password not accepted"
- ✅ Make sure you're using an App Password, not your regular password
- ✅ Remove any spaces from the app password
- ✅ Verify 2FA is enabled on your Google account

### Error: "SMTPAuthenticationError"
- ✅ Double-check your email and app password
- ✅ Make sure environment variables are set correctly
- ✅ Try generating a new app password

### Error: "Connection refused"
- ✅ Check your firewall settings
- ✅ Verify MAIL_SERVER and MAIL_PORT are correct
- ✅ Try using port 465 with SSL instead of 587 with TLS

### No Error but Email Not Received
- ✅ Check spam/junk folder
- ✅ Verify recipient email is valid
- ✅ Check Gmail "Sent" folder to confirm it was sent

### "Email notifications disabled" message
- ✅ This means MAIL_USERNAME or MAIL_PASSWORD is not set
- ✅ Set the environment variables and restart the app

---

## 📝 Current Configuration

The app now:
- ✅ Checks if email is configured before attempting to send
- ✅ Provides clear feedback about email status
- ✅ Continues working even if email fails
- ✅ Sends beautifully formatted emails with emojis
- ✅ Includes all incident details in the email

---

## 🎯 Quick Start (Copy-Paste)

**For Gmail users:**

1. Get your app password from: https://myaccount.google.com/apppasswords

2. Run these commands (replace with your details):
```powershell
$env:MAIL_USERNAME="your-email@gmail.com"
$env:MAIL_PASSWORD="xxxx xxxx xxxx xxxx"
py app.py
```

That's it! 🎉

---

## 💡 Pro Tips

1. **Use a dedicated email** - Create a separate Gmail account for WARRN notifications
2. **Test first** - Always test with your own email before going live
3. **Monitor logs** - Check console output for email errors
4. **Backup plan** - The app works fine without email, it's just a notification feature

---

## 🆘 Still Having Issues?

Common fixes:
1. Restart your terminal after setting environment variables
2. Make sure there are no quotes around the password
3. Try removing spaces from the app password
4. Verify you're using the correct Gmail account
5. Check if Gmail is blocking the login attempt (check your email for security alerts)
