# Wrestling Data Hub

A comprehensive NCAA D1 Wrestling Championship data platform built with Python FastAPI backend and React frontend.

## Features

- **Home Page**: Overview of the platform and its capabilities
- **Wrestler Profiles**: Detailed wrestler information including statistics, match history, and career highlights
- **School Programs**: Wrestling program information, team statistics, coaching staff, and rosters
- **Interactive Brackets**: Tournament brackets using react-brackets for NCAA championships
- **Advanced Search**: Search across wrestlers, schools, and coaches with filtering options
- **Coach Profiles**: Coaching staff information and experience

## Tech Stack

### Backend
- **Python 3.9+**
- **FastAPI**: Modern, fast web framework for building APIs
- **PostgreSQL**: Database (via Supabase)
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations
- **Pydantic**: Data validation and serialization

### Frontend
- **React 18**: Frontend framework
- **Material-UI (MUI)**: UI component library
- **React Router**: Client-side routing
- **React Query**: Data fetching and caching
- **React Brackets**: Tournament bracket visualization
- **Axios**: HTTP client

## Project Structure

```
louden-swain/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models and Pydantic schemas
│   │   ├── routers/         # API route handlers
│   │   ├── services/        # Business logic
│   │   ├── database/        # Database configuration
│   │   ├── config.py        # Application configuration
│   │   └── main.py          # FastAPI application entry point
│   ├── alembic/             # Database migrations
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variables example
├── frontend/
│   ├── src/
│   │   ├── components/      # Reusable React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API service functions
│   │   ├── hooks/           # Custom React hooks
│   │   ├── App.js           # Main App component
│   │   └── index.js         # React entry point
│   ├── public/              # Static assets
│   └── package.json         # Node.js dependencies
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 16+
- PostgreSQL database (or Supabase account)

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and configuration
   ```

5. Run database migrations:
   ```bash
   alembic upgrade head
   ```

6. Start the development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

The frontend will be available at http://localhost:3000 and will proxy API requests to the backend at http://localhost:8000.

## Database Schema

The application includes the following main entities:

- **Wrestlers**: Athlete profiles with personal information and statistics
- **Schools**: Wrestling programs and institutional information
- **Coaches**: Coaching staff details and experience
- **Tournaments**: Competition events and details
- **Brackets**: Tournament bracket structure and data
- **Matches**: Individual match results and statistics

## API Endpoints

### Wrestlers
- `GET /api/wrestlers` - List wrestlers with filtering
- `GET /api/wrestlers/{id}` - Get wrestler details
- `GET /api/wrestlers/{id}/stats` - Get wrestler statistics
- `POST /api/wrestlers` - Create new wrestler
- `PUT /api/wrestlers/{id}` - Update wrestler
- `DELETE /api/wrestlers/{id}` - Delete wrestler

### Schools
- `GET /api/schools` - List schools with filtering
- `GET /api/schools/{id}` - Get school details
- `GET /api/schools/{id}/stats` - Get school statistics
- `POST /api/schools` - Create new school
- `PUT /api/schools/{id}` - Update school
- `DELETE /api/schools/{id}` - Delete school

### Brackets
- `GET /api/brackets/tournament/{tournament_id}` - Get tournament brackets
- `GET /api/brackets/{id}` - Get bracket details
- `GET /api/brackets/{id}/data` - Get bracket data for react-brackets
- `POST /api/brackets` - Create new bracket
- `PUT /api/brackets/{id}/data` - Update bracket data

### Search
- `GET /api/search` - Search across all entities
- `GET /api/search/wrestlers` - Search wrestlers specifically
- `GET /api/search/schools` - Search schools specifically

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NCAA for wrestling championship data
- React Brackets library for bracket visualization
- FastAPI and React communities for excellent documentation and tools
