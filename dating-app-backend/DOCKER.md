# Docker Setup for Dating App Backend

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# 1. Create .env file from example
cp .env.example .env

# 2. Start services (MongoDB + FastAPI)
docker-compose up -d

# 3. Check logs
docker-compose logs -f app

# 4. Access API
# Swagger API docs: http://localhost:8000/docs
# ReDoc docs: http://localhost:8000/redoc
```

### Option 2: Using Docker CLI

```bash
# Build the image
docker build -t dating-app:latest .

# Run the container
docker run -d \
  --name dating_app_backend \
  -p 8000:8000 \
  -e MONGODB_URI=mongodb://localhost:27017 \
  -e JWT_SECRET_KEY=your-secret-key \
  dating-app:latest
```

---

## Environment Variables

The Docker container uses the following environment variables (see `docker-compose.yml` for defaults):

| Variable | Default | Description |
|----------|---------|-------------|
| `MONGODB_URI` | `mongodb://admin:changeme@mongodb:27017/dating_app` | MongoDB connection string |
| `JWT_SECRET_KEY` | | JWT secret key for token signing |
| `DEBUG` | `false` | Enable/disable debug mode |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:8000` | Allowed CORS origins |
| `CLOUDINARY_*` | | Image storage configuration |

---

## Common Commands

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Remove volume data
docker-compose down -v

# View logs
docker-compose logs -f app
docker-compose logs -f mongodb

# Rebuild image
docker-compose up --build

# Run a single service
docker-compose up mongodb
docker-compose up app

# Execute command in container
docker-compose exec app bash
```

---

## Production Deployment

### Security Recommendations

1. **Change secrets in `.env`:**
   ```bash
   JWT_SECRET_KEY=<generate-random-secure-key>
   MONGO_ROOT_PASSWORD=<strong-password>
   SECRET_KEY=<generate-random-secure-key>
   ```

2. **Use environment-specific configs:**
   - Create `.env.production`
   - Set `DEBUG=false`
   - Use production MongoDB URI or MongoDB Atlas

3. **Network configuration:**
   - Don't expose MongoDB port in production
   - Use reverse proxy (nginx) in front of FastAPI
   - Enable HTTPS/SSL

### Example Production Deployment

```bash
# Load production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Troubleshooting

### MongoDB Connection Failed

```bash
# Check MongoDB is running
docker-compose logs mongodb

# Verify connection string matches service name
# Use: mongodb://mongodb:27017 (from app container)
# Not: mongodb://localhost:27017
```

### Port Already in Use

```bash
# Change ports in docker-compose.yml
# Or kill the process using the port
lsof -i :8000  # Find process
kill -9 <PID>  # Kill it
```

### Rebuild After Code Changes

```bash
docker-compose up --build
```

### Access MongoDB from Container

```bash
docker-compose exec mongodb mongosh -u admin -p changeme --authenticationDatabase admin
```

---

## Health Checks

The Docker setup includes health checks:
- **FastAPI**: Checks `/docs` endpoint every 30 seconds
- **MongoDB**: Runs `ping` command every 10 seconds

View health status:
```bash
docker-compose ps
```

---

## Docker Images

- **FastAPI App**: `dating-app:latest` (Python 3.11-slim, ~500MB)
- **MongoDB**: `mongo:7.0` (official MongoDB image)

---

## Additional Resources

- [FastAPI Docker Documentation](https://fastapi.tiangolo.com/deployment/docker/)
- [MongoDB Docker Documentation](https://hub.docker.com/_/mongo)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
