# KodBank - Digital Banking Application

A full-stack banking application with user registration, login, balance check, and money transfer features.

## Features

- ✅ User Registration with email, userid, phone number
- ✅ Secure Login with JWT authentication
- ✅ **Check Balance** - Verifies logged-in user's balance from database
- ✅ Transfer Money to other users
- ✅ Transaction History
- ✅ Modern Dark UI Design
- ✅ Token-based Authentication (stored in localStorage)
- ✅ Chatbot Assistant

## Local Development

### Prerequisites
- Python 3.8 or higher installed

### Running Locally
1. Open terminal in the KodBank folder
2. Run: `pip install -r requirements.txt`
3. Run: `python app.py`
4. Open browser to: **http://127.0.0.1:5000**

## Vercel Deployment

### Files for Vercel
- `vercel.json` - Vercel configuration
- `runtime.txt` - Python version (python-3.11)
- `app.py` - Flask application
- `templates/index.html` - Frontend

### Deploy Steps
1. Push code to GitHub
2. Go to [Vercel.com](https://vercel.com)
3. Import your GitHub repository
4. Vercel will automatically detect Flask app
5. Deploy!

### Note on Database
Vercel's serverless functions have limited filesystem. The database will be stored in `/tmp/` which is temporary. Data may be lost on function cold starts. For production, use a cloud database like PostgreSQL or MongoDB.

## How to Use

### Registration
1. Click "Register" on the login page
2. Fill in your details (full name, userid, email, phone, password)
3. Click Register

### Login
1. Enter your User ID and Password
2. Click Login

### Check Balance
1. After login, click **"Check Balance"** in the header
2. The system fetches your balance from the database using JWT token
3. Shows your verified User ID and Email

### Transfer Money
1. Click **"Transfer"** in the header
2. Enter recipient's User ID
3. Enter amount to transfer
4. Confirm the transfer

## Default Balance
New users get **$10,000** for testing.

## Project Structure
```
KodBank/
├── app.py              # Flask backend
├── requirements.txt    # Dependencies
├── vercel.json         # Vercel config
├── runtime.txt        # Python version
├── templates/
│   └── index.html     # Frontend UI
├── instance/
│   └── kodbank.db    # SQLite database (local only)
