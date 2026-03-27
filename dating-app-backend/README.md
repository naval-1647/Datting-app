# Dating App Backend

A production-ready Dating App Backend built with FastAPI and MongoDB. Features JWT authentication, real-time chat via WebSockets, intelligent matching algorithm, swipe/match system, and notifications.

## 🚀 Features

### Core Functionality
- ✅ **JWT Authentication** - Access & refresh tokens with bcrypt password hashing
- ✅ **User Profiles** - Complete CRUD operations with image uploads
- ✅ **Swipe System** - Like/dislike with duplicate prevention
- ✅ **Matching Algorithm** - Location-based, age preferences, common interests
- ✅ **Real-time Chat** - WebSocket support with typing indicators & online status
- ✅ **Notifications** - Match and message notifications
- ✅ **Image Upload** - Cloudinary or local storage support

### Security & Performance
- ✅ Rate limiting (brute-force protection)
- ✅ CORS middleware
- ✅ Input validation with Pydantic
- ✅ Geo-spatial queries for proximity matching
- ✅ Pagination & filtering
- ✅ Comprehensive error handling

### API Documentation
- ✅ Auto-generated Swagger UI at `/docs`
- ✅ ReDoc at `/redoc`
- ✅ Example request/response bodies

---

## 📁 Project Structure

```
dating-app-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app initialization
│   ├── config.py               # Configuration & environment variables
│   ├── database.py             # MongoDB connection (Motor)
│   ├── dependencies.py         # Dependency injection (auth, rate limiting)
│   ├── middleware.py           # Custom middleware & exceptions
│   ├── websocket.py            # WebSocket connection manager
│   │
│   ├── models/                 # Database models
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── swipe.py
│   │   ├── match.py
│   │   └── message.py
│   │
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── profile.py
│   │   ├── swipe.py
│   │   ├── match.py
│   │   ├── message.py
│   │   └── token.py
│   │
│   ├── routers/                # API endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── profiles.py
│   │   ├── swipes.py
│   │   ├── matches.py
│   │   ├── chat.py
│   │   └── notifications.py
│   │
│   └── services/               # Business logic
│       ├── auth_service.py
│       ├── user_service.py
│       ├── profile_service.py
│       ├── swipe_service.py
│       ├── match_service.py
│       ├── message_service.py
│       ├── notification_service.py
│       └── storage_service.py
│
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.9+
- MongoDB 4.4+ (local or Atlas)
- pip or poetry

### 1. Clone Repository
```bash
cd dating-app-backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your credentials
```

### 5. Configure MongoDB
Update `MONGODB_URI` in `.env`:
```env
# Local MongoDB
MONGODB_URI=mongodb://localhost:27017

# OR MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/dating_app
```

### 6. Run the Application
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/signup` | Register new user |
| POST | `/api/v1/auth/login` | Login (get tokens) |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| GET | `/api/v1/auth/me` | Get current user |
| POST | `/api/v1/auth/logout` | Logout |

### Profile
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/profiles/` | Create profile |
| GET | `/api/v1/profiles/me` | Get my profile |
| PUT | `/api/v1/profiles/me` | Update profile |
| POST | `/api/v1/profiles/me/images` | Upload images |
| DELETE | `/api/v1/profiles/me/images/{index}` | Delete image |
| GET | `/api/v1/profiles/{user_id}` | Get user profile |

### Swipes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/swipes/` | Swipe (like/dislike) |
| GET | `/api/v1/swipes/suggestions` | Get suggested users |
| GET | `/api/v1/swipes/history` | Get swipe history |
| GET | `/api/v1/swipes/check/{user_id}` | Check swipe status |

### Matches
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/matches/` | Get all matches |
| GET | `/api/v1/matches/{match_id}` | Get specific match |
| DELETE | `/api/v1/matches/{match_id}` | Unmatch |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| WS | `/api/v1/chat/ws/{match_id}` | WebSocket chat |
| GET | `/api/v1/chat/{match_id}/history` | Get messages |
| POST | `/api/v1/chat/{match_id}/messages` | Send message (REST) |
| POST | `/api/v1/chat/{match_id}/read` | Mark as read |

### Notifications
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/notifications/` | Get notifications |
| GET | `/api/v1/notifications/unread-count` | Get unread count |
| PUT | `/api/v1/notifications/{id}/read` | Mark as read |
| PUT | `/api/v1/notifications/read-all` | Mark all as read |
| DELETE | `/api/v1/notifications/{id}` | Delete notification |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/search` | Search users |
| GET | `/api/v1/users/` | List all users |

---

## 📝 Example Requests

### Signup
```bash
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### Create Profile
```bash
curl -X POST http://localhost:8000/api/v1/profiles/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "age": 28,
    "gender": "male",
    "bio": "Love hiking and photography",
    "interests": ["hiking", "photography", "travel"],
    "location": {
      "type": "Point",
      "coordinates": [-73.935242, 40.730610]
    }
  }'
```

### Swipe (Like)
```bash
curl -X POST http://localhost:8000/api/v1/swipes/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target_user_id": "USER_ID_TO_SWIPE",
    "action": "like"
  }'
```

### Get Suggestions
```bash
curl -X GET "http://localhost:8000/api/v1/swipes/suggestions?limit=20" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# MongoDB
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=dating_app

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Image Storage
STORAGE_TYPE=local  # or 'cloudinary'
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# Security
SECRET_KEY=your-secret-key-for-password-hashing

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
LOGIN_RATE_LIMIT_PER_MINUTE=5
```

---

## 🗄️ Database Collections

### users
- email, hashed_password, is_active, created_at

### profiles
- user_id, name, age, gender, bio, interests, location (GeoJSON), images[]

### swipes
- user_id, target_user_id, action (like/dislike), created_at

### matches
- user1_id, user2_id, created_at, matched_at

### messages
- match_id, sender_id, receiver_id, content, is_read, timestamp

### notifications
- user_id, type, title, data, is_read, created_at

---

## 🚢 Deployment

### Deploy to Render/Railway

1. **Create `Dockerfile`**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Set Environment Variables** in platform dashboard

3. **Connect MongoDB Atlas** using connection string

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/ -v
```

---

## 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Features interactive API documentation with try-it-out functionality.

---

## 🔐 Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Rate limiting to prevent brute-force attacks
- CORS configuration
- Input validation with Pydantic
- HTML sanitization
- Protected routes with dependency injection

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 💡 Support

For issues or questions:
- Create an issue on GitHub
- Check API documentation at `/docs`
- Review example requests in this README

---

## 🎯 Key Features Highlights

### Matching Algorithm
The app suggests users based on:
- **Proximity** (40% weight) - Uses MongoDB geo-spatial queries
- **Common Interests** (40% weight) - Array intersection scoring
- **Activity Level** (20% weight) - Recent activity bonus

### Real-time Chat
- WebSocket-based communication
- Typing indicators
- Online/offline status
- Message read receipts
- Automatic notifications for offline users

### Image Upload
- Supports multiple images per profile
- Cloudinary integration (recommended) or local storage
- Automatic image optimization
- Delete functionality included

---

**Built with ❤️ using FastAPI and MongoDB**
