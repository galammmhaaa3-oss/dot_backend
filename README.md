# DOT Backend API

Backend API for DOT (خدمات التوصيل والنقل) - A taxi and delivery service application.

## Features

- 🚕 **Taxi Service**: Request rides with automatic price calculation
- 📦 **Delivery Service**: Create delivery requests with detailed tracking
- 🔐 **Authentication**: JWT-based secure authentication
- 👤 **User Management**: Profile management and history tracking
- 💰 **Automatic Pricing**: Distance-based pricing for rides and deliveries
- 🌍 **Location Services**: Haversine distance calculation

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT (python-jose)
- **Deployment**: Render (Free Tier)

## Project Structure

```
dot_backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Core utilities (security, pricing)
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── utils/            # Helper functions
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   └── main.py           # FastAPI app
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── render.yaml          # Render deployment config
└── .env.example         # Environment variables template
```

## Local Development

### Prerequisites

- Python 3.11+
- PostgreSQL

### Setup

1. **Clone the repository**

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access the API**
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get JWT token

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile

### Rides (Taxi Service)
- `POST /api/v1/rides` - Create ride request
- `GET /api/v1/rides/{ride_id}` - Get ride details
- `GET /api/v1/rides` - Get user's ride history
- `PATCH /api/v1/rides/{ride_id}/status` - Update ride status

### Deliveries
- `POST /api/v1/deliveries` - Create delivery request
- `GET /api/v1/deliveries/{delivery_id}` - Get delivery details
- `GET /api/v1/deliveries` - Get user's delivery history
- `PATCH /api/v1/deliveries/{delivery_id}/status` - Update delivery status

## Deployment on Render

### Automatic Deployment (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml` and create services

3. **Access your API**
   - Your API will be available at: `https://dot-api.onrender.com`
   - Documentation: `https://dot-api.onrender.com/docs`

### Manual Deployment

1. **Create PostgreSQL Database**
   - Go to Render Dashboard
   - Click "New" → "PostgreSQL"
   - Name: `dot-db`
   - Copy the Internal Database URL

2. **Create Web Service**
   - Click "New" → "Web Service"
   - Connect your repository
   - Settings:
     - Name: `dot-api`
     - Environment: `Python 3`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Add Environment Variables**
   - `DATABASE_URL`: (Paste Internal Database URL)
   - `SECRET_KEY`: (Generate random key)
   - `ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `10080`
   - `CORS_ORIGINS`: `*`

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment to complete

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-here` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `10080` (7 days) |
| `CORS_ORIGINS` | Allowed CORS origins | `*` or `https://yourdomain.com` |
| `DEBUG` | Debug mode | `False` |

## Pricing Logic

### Taxi Service
- Minimum fare: 10,000 SYP
- Per kilometer: 5,000 SYP
- Formula: `max(10000, distance_km * 5000)`

### Delivery Service
- Delivery fee: Same as taxi
- Product amount: Added if driver pays
- Formula: `delivery_fee + (product_amount if driver_pays else 0)`

## Future Enhancements

- [ ] Driver app integration
- [ ] Admin panel
- [ ] Real-time location tracking (WebSockets)
- [ ] Push notifications
- [ ] Payment gateway integration
- [ ] Rating and review system
- [ ] Advanced analytics

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.
