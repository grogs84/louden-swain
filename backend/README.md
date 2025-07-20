# Wrestling Tournament Management API

A modern FastAPI backend for wrestling tournament management with PostgreSQL database, JWT authentication, and comprehensive testing infrastructure.

## Technology Stack

- **Framework**: Python 3.11+ with FastAPI
- **Database**: PostgreSQL with asyncpg driver
- **ORM**: SQLAlchemy 2.0+ with Alembic migrations
- **Authentication**: Python-JOSE for JWT tokens
- **Validation**: Pydantic for request/response models
- **Testing**: pytest with pytest-asyncio
- **Deployment**: Railway ready

## Project Structure

```
backend/
├── src/
│   ├── main.py                 # FastAPI app entry point
│   ├── api/                    # API endpoints
│   │   ├── auth/               # Authentication endpoints
│   │   ├── tournaments/        # Tournament CRUD endpoints
│   │   ├── matches/            # Match management endpoints
│   │   ├── participants/       # Participant endpoints
│   │   └── admin/              # Admin-specific endpoints
│   ├── core/                   # Core functionality
│   │   ├── config.py           # Configuration management
│   │   ├── security.py         # JWT and password handling
│   │   └── database.py         # Database connection
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic request/response models
│   ├── services/               # Business logic
│   └── migrations/             # Alembic database migrations
├── tests/                      # Test suites
│   ├── conftest.py
│   ├── test_api/
│   ├── test_models/
│   └── test_services/
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── Dockerfile                  # Railway deployment
├── railway.toml               # Railway configuration
├── alembic.ini                # Alembic configuration
├── .env.example               # Environment variables example
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL database
- Git

### Local Development Setup

1. **Clone and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

5. **Initialize database:**
   ```bash
   alembic upgrade head
   ```

6. **Start development server:**
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname

# JWT Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# Admin User
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=secure-admin-password

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Environment
ENVIRONMENT=development
```

## API Documentation

Once the server is running, visit:

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## API Response Format

All API responses follow this standardized format:

```json
{
  "data": {...},
  "meta": {
    "timestamp": "2025-07-20T11:00:55Z",
    "version": "1.0"
  },
  "errors": [...] // if applicable
}
```

## Development Workflow

### Code Quality

Run code quality checks:

```bash
# Format code
black src tests

# Sort imports
isort src tests

# Lint code
flake8 src tests
```

### Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_api/test_auth.py
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1
```

### Pre-commit Hooks

Set up pre-commit hooks for automated code quality:

```bash
pre-commit install
```

## Deployment

### Railway Deployment

The application is configured for Railway deployment:

1. **Build**: Automatic with Dockerfile
2. **Environment**: Set environment variables in Railway dashboard
3. **Health Check**: `/health` endpoint configured
4. **Port**: Automatically configured by Railway

### Docker

Build and run with Docker:

```bash
# Build image
docker build -t wrestling-api .

# Run container
docker run -p 8000:8000 --env-file .env wrestling-api
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `POST /api/auth/refresh` - Token refresh

### Tournaments
- `GET /api/tournaments` - List tournaments
- `GET /api/tournaments/{id}` - Get tournament details
- `POST /api/tournaments` - Create tournament
- `PUT /api/tournaments/{id}` - Update tournament
- `DELETE /api/tournaments/{id}` - Delete tournament

### Matches
- `GET /api/matches` - List matches
- `GET /api/matches/{id}` - Get match details
- `POST /api/matches` - Create match
- `PUT /api/matches/{id}` - Update match
- `DELETE /api/matches/{id}` - Delete match

### Participants
- `GET /api/participants` - List participants
- `GET /api/participants/{id}` - Get participant details
- `POST /api/participants` - Create participant
- `PUT /api/participants/{id}` - Update participant
- `DELETE /api/participants/{id}` - Delete participant

### Admin
- `GET /api/admin/users` - List users (admin only)
- `GET /api/admin/system/health` - System health (admin only)
- `POST /api/admin/data/import` - Import data (admin only)
- `POST /api/admin/data/export` - Export data (admin only)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run code quality checks: `black src tests && isort src tests && flake8 src tests`
5. Run tests: `pytest`
6. Commit your changes: `git commit -m 'Add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

## License

This project is licensed under the MIT License.
