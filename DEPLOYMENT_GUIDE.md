# 🚀 WARRN Deployment Guide for Render

## ✅ What Works on Render:
- ✅ PostgreSQL Database (Free)
- ✅ Email Sending (Gmail SMTP)
- ✅ File Uploads (with Cloudinary)
- ✅ WebSockets
- ✅ All Features

---

## 📋 Pre-Deployment Checklist:

### 1. Gmail App Password
- Go to: https://myaccount.google.com/apppasswords
- Enable 2FA
- Generate app password
- Save it (you'll need it)

### 2. GitHub Repository
- Create new repo on GitHub
- Push your code

---

## 🚀 Deployment Steps:

### Step 1: Push to GitHub

```bash
cd warrn_project
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

### Step 2: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render

### Step 3: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Name: `warrn-db`
3. Database: `warrn`
4. User: `warrn`
5. Region: Oregon (Free)
6. Click "Create Database"
7. **Copy the Internal Database URL** (starts with `postgresql://`)

### Step 4: Create Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repo
3. Settings:
   - **Name:** `warrn`
   - **Region:** Oregon (Free)
   - **Branch:** main
   - **Root Directory:** (leave empty)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --worker-class eventlet -w 1 app:app`
   - **Instance Type:** Free

### Step 5: Add Environment Variables

Click "Environment" tab and add:

```
DATABASE_URL = [paste the Internal Database URL from Step 3]
SECRET_KEY = [any random string, e.g., your-secret-key-12345]
MAIL_SERVER = smtp.gmail.com
MAIL_PORT = 587
MAIL_USERNAME = your-email@gmail.com
MAIL_PASSWORD = your-16-char-app-password
PYTHON_VERSION = 3.10.0
```

### Step 6: Deploy!
1. Click "Create Web Service"
2. Wait 5-10 minutes for deployment
3. Your app will be live at: `https://warrn.onrender.com`

---

## 📧 Email Configuration:

Your email settings are already in the code:
```python
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
```

Just set the environment variables in Render dashboard!

---

## 💾 Database Configuration:

Your code already handles PostgreSQL:
```python
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
```

Render automatically provides `DATABASE_URL`!

---

## 📁 File Uploads (Images):

**Issue:** Render's filesystem is ephemeral (files deleted on restart)

**Solution:** Use Cloudinary (Free)

### Option 1: Keep Current Setup (Simple)
- Files will work but may be lost on restart
- Good for testing
- No changes needed

### Option 2: Use Cloudinary (Production)
1. Sign up: https://cloudinary.com (Free)
2. Get API credentials
3. Add to environment variables:
   ```
   CLOUDINARY_CLOUD_NAME=your-cloud-name
   CLOUDINARY_API_KEY=your-api-key
   CLOUDINARY_API_SECRET=your-api-secret
   ```
4. Update code to use Cloudinary (I can help with this)

---

## 🧪 After Deployment:

### 1. Create Admin User
Visit: `https://your-app.onrender.com`

Register first user (will be admin automatically)

### 2. Test Features
- ✅ Submit report
- ✅ Check email notifications
- ✅ Login as responder
- ✅ Claim and resolve reports
- ✅ Check admin panel

---

## 🔧 Troubleshooting:

### Database Connection Error
- Check `DATABASE_URL` is set correctly
- Make sure it starts with `postgresql://` not `postgres://`

### Email Not Sending
- Verify `MAIL_USERNAME` and `MAIL_PASSWORD` are set
- Check Gmail app password is correct
- Look at Render logs for errors

### App Not Starting
- Check Render logs
- Verify `requirements.txt` has all dependencies
- Make sure `gunicorn` is in requirements.txt

### Images Not Showing
- This is normal on Render (ephemeral filesystem)
- Use Cloudinary for production

---

## 📊 Render Free Tier Limits:

- ✅ 750 hours/month (enough for 1 app)
- ✅ PostgreSQL database (1GB)
- ✅ Automatic SSL
- ✅ Custom domain support
- ⚠️ App sleeps after 15 min inactivity (wakes on request)

---

## 🎯 Quick Commands:

### View Logs
Go to Render dashboard → Your service → Logs

### Restart App
Render dashboard → Your service → Manual Deploy → Deploy latest commit

### Update Environment Variables
Render dashboard → Your service → Environment → Add/Edit

---

## 🆘 Need Help?

Common issues:
1. **App sleeping:** Free tier sleeps after 15 min. First request takes 30 sec to wake up.
2. **Database connection:** Make sure DATABASE_URL is set correctly.
3. **Email not working:** Verify Gmail app password and environment variables.

---

## ✅ Deployment Checklist:

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] PostgreSQL database created
- [ ] Web service created
- [ ] Environment variables set (DATABASE_URL, MAIL_*, SECRET_KEY)
- [ ] App deployed successfully
- [ ] Admin user created
- [ ] Email tested
- [ ] All features working

---

**Your app will be live at:** `https://warrn.onrender.com` (or your custom domain)

**Deployment time:** ~10 minutes

**Cost:** FREE! 🎉
