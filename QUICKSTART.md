# Quick Start Guide

## For Render Deployment (Recommended)

### 1. Push to GitHub
```bash
cd C:\Users\ABDULLAH\Desktop\DOT_1\dot_backend
git init
git add .
git commit -m "Initial backend commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Deploy on Render
1. Go to https://dashboard.render.com
2. Click "New" → "Blueprint"
3. Connect your GitHub repository
4. Select the repository with `dot_backend`
5. Render will automatically detect `render.yaml` and create:
   - PostgreSQL database (`dot-db`)
   - Web service (`dot-api`)

### 3. Access Your API
- API URL: `https://dot-api.onrender.com`
- Documentation: `https://dot-api.onrender.com/docs`
- Health Check: `https://dot-api.onrender.com/health`

### 4. Update Flutter App
In your Flutter app, update the API base URL:
```dart
const String API_BASE_URL = "https://dot-api.onrender.com/api/v1";
```

---

## For Local Testing

### 1. Install Python 3.11+
Download from: https://www.python.org/downloads/

### 2. Create Virtual Environment
```bash
cd C:\Users\ABDULLAH\Desktop\DOT_1\dot_backend
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup PostgreSQL (Optional - Use SQLite for testing)
For quick testing, update `.env`:
```
DATABASE_URL=sqlite:///./dot.db
```

### 5. Run the Server
```bash
uvicorn app.main:app --reload
```

### 6. Test the API
- Open browser: http://localhost:8000/docs
- Try the endpoints!

---

## API Testing Examples

### 1. Register User
```bash
POST http://localhost:8000/api/v1/auth/register
{
  "phone": "0912345678",
  "name": "Test User",
  "password": "password123"
}
```

### 2. Login
```bash
POST http://localhost:8000/api/v1/auth/login
{
  "phone": "0912345678",
  "password": "password123"
}
```

### 3. Create Ride (Use token from login)
```bash
POST http://localhost:8000/api/v1/rides
Authorization: Bearer <your-token>
{
  "pickup_lat": 36.2021,
  "pickup_lng": 37.1343,
  "pickup_address": "Aleppo, Syria",
  "destination_lat": 36.2100,
  "destination_lng": 37.1500,
  "destination_address": "Aleppo University"
}
```

---

## Next Steps

1. ✅ Backend is ready for deployment
2. 🔄 Deploy to Render (free)
3. 📱 Update Flutter app with API URL
4. 🧪 Test all features
5. 🚀 Launch!
