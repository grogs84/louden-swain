# Development Guide

## Quick Start

### Option 1: Using the Setup Script
```bash
./setup.sh
```

### Option 2: Manual Setup

#### Backend Setup
1. Create and activate virtual environment:
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. Initialize database:
   ```bash
   alembic upgrade head
   ```

5. Start development server:
   ```bash
   uvicorn app.main:app --reload
   ```

#### Frontend Setup
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   ```

3. Start development server:
   ```bash
   npm start
   ```

### Option 3: Using Docker
```bash
docker-compose up -d
```

## Development Workflow

### Database Migrations
Create a new migration:
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
```

Apply migrations:
```bash
alembic upgrade head
```

### Adding New API Endpoints
1. Define models in `backend/app/models/models.py`
2. Create Pydantic schemas in `backend/app/models/schemas.py`
3. Implement router in `backend/app/routers/`
4. Add router to main app in `backend/app/main.py`

### Adding New React Pages
1. Create page component in `frontend/src/pages/`
2. Add route to `frontend/src/App.js`
3. Create API service functions in `frontend/src/services/api.js`

### Project Structure Details

```
backend/app/
├── models/
│   ├── models.py       # SQLAlchemy database models
│   └── schemas.py      # Pydantic schemas for API
├── routers/
│   ├── wrestlers.py    # Wrestler-related endpoints
│   ├── schools.py      # School-related endpoints
│   ├── coaches.py      # Coach-related endpoints
│   ├── tournaments.py  # Tournament-related endpoints
│   ├── brackets.py     # Bracket-related endpoints
│   └── search.py       # Search endpoints
├── database/
│   └── database.py     # Database configuration
├── config.py           # Application configuration
└── main.py            # FastAPI application entry

frontend/src/
├── components/
│   └── Navbar.js       # Navigation component
├── pages/
│   ├── HomePage.js     # Landing page
│   ├── WrestlerPage.js # Individual wrestler profile
│   ├── SchoolPage.js   # School program page
│   ├── BracketsPage.js # Tournament brackets
│   └── SearchPage.js   # Search interface
└── services/
    └── api.js          # API service functions
```

## API Documentation
Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

## Database Schema

### Core Entities
- **Wrestlers**: Personal info, weight class, school affiliation
- **Schools**: Program details, location, conference
- **Coaches**: Staff information, position, experience
- **Tournaments**: Competition details, dates, location
- **Brackets**: Tournament structure, match progression
- **Matches**: Individual bout results and statistics

### Key Relationships
- Wrestlers belong to Schools
- Coaches work at Schools
- Brackets belong to Tournaments
- Matches are part of Brackets
- Matches involve Wrestlers

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Production Environment Variables
Backend (.env):
```
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
SECRET_KEY=your-production-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Frontend (.env):
```
REACT_APP_API_URL=https://your-api-domain.com/api
```

### Docker Production Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Common Issues

### Backend Issues
- **Import errors**: Make sure virtual environment is activated
- **Database connection**: Check DATABASE_URL in .env
- **Migration errors**: Ensure database is running and accessible

### Frontend Issues
- **API calls failing**: Check REACT_APP_API_URL in .env
- **CORS errors**: Verify backend CORS configuration
- **Build errors**: Clear node_modules and reinstall

### Docker Issues
- **Port conflicts**: Make sure ports 3000, 8000, 5432 are available
- **Database not ready**: Wait for health check to pass

## Contributing

1. Follow PEP 8 for Python code
2. Use Prettier for JavaScript/React code
3. Write tests for new features
4. Update documentation for API changes
5. Use meaningful commit messages
