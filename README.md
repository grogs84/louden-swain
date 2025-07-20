# Louden Swain - Wrestling Tournament Management Platform

A comprehensive NCAA D1 wrestling data platform featuring wrestler profiles, tournament brackets, school information, and search functionality. Built with a modern tech stack including Next.js frontend and FastAPI backend.

## 🏗️ Project Architecture

### Frontend (Next.js)
- **Framework**: Next.js 15.4.2 with React 18
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **API Client**: TanStack Query (React Query)
- **Components**: Custom UI components with shadcn/ui styling
- **TypeScript**: Full type safety

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.12
- **Database**: Supabase PostgreSQL with asyncpg
- **Authentication**: JWT-based auth with python-jose
- **ORM**: Raw SQL with asyncpg for high performance
- **Migration**: Alembic for database migrations
- **Environment**: Pydantic settings management

### Database
- **Primary**: Supabase PostgreSQL
- **Connection**: Async connection pooling
- **Schema**: Wrestling-specific entities (wrestlers, schools, tournaments, matches)

## 🚀 Getting Started

### Prerequisites
- Python 3.12+
- Node.js 18+
- npm or yarn
- Supabase account (for database)

### Environment Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/grogs84/louden-swain.git
   cd louden-swain
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   ```

4. **Environment Configuration**
   
   **Backend** - Create `backend/.env`:
   ```env
   # Database (Supabase PostgreSQL)
   DATABASE_URL=postgresql+asyncpg://[username]:[password]@[host]:5432/postgres
   
   # Supabase
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   
   # JWT Security
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   JWT_EXPIRE_MINUTES=30
   
   # Admin User
   ADMIN_EMAIL=admin@example.com
   ADMIN_PASSWORD=admin123
   
   # Next.js Environment Variables (for backend reference)
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   ```
   
   **Frontend** - Create `frontend/.env.local`:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

### Development Setup

1. **Start Backend Server**
   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start Frontend Server** (in a new terminal)
   ```bash
   # From project root
   npm run dev
   # Or from frontend directory
   cd frontend && npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📁 Project Structure

```
louden-swain/
├── README.md
├── package.json                 # Root package.json with workspace scripts
├── railway.json                 # Railway deployment config
├── requirements.txt             # Python requirements (legacy)
├── setup.sh                     # Setup script
├── SUPABASE_SCHEMA.md          # Database schema documentation
│
├── backend/                     # FastAPI Backend
│   ├── .env.example
│   ├── .env                     # Environment variables
│   ├── alembic.ini             # Database migration config
│   ├── Dockerfile              # Container config
│   ├── pyproject.toml          # Python project config
│   ├── requirements.txt        # Python dependencies
│   ├── venv/                   # Python virtual environment
│   │
│   ├── app/                    # Main application
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app entry point
│   │   ├── config.py           # Configuration management
│   │   ├── database.py         # Database connection & utilities
│   │   ├── models.py           # Data models
│   │   └── routers/            # API route handlers
│   │       ├── __init__.py
│   │       ├── schools.py
│   │       ├── search.py
│   │       ├── tournaments.py
│   │       └── wrestlers.py
│   │
│   ├── src/                    # Alternative source structure
│   │   ├── main.py
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core functionality
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   │
│   └── tests/                 # Test suite
│       ├── conftest.py
│       ├── test_main.py
│       └── test_api/
│
└── frontend/                   # Next.js Frontend
    ├── .env.local             # Environment variables
    ├── package.json           # Frontend dependencies
    ├── next.config.js         # Next.js configuration
    ├── tailwind.config.js     # Tailwind CSS config
    ├── tsconfig.json          # TypeScript config
    ├── node_modules/          # Node dependencies
    │
    ├── public/                # Static assets
    │   └── index.html
    │
    └── src/                   # Source code
        ├── app/               # App Router (Next.js 13+)
        │   ├── layout.tsx     # Root layout
        │   ├── page.tsx       # Home page
        │   ├── browse/        # Browse page
        │   ├── profile/       # Wrestler profiles
        │   └── tournament/    # Tournament pages
        │
        ├── components/        # React components
        │   ├── search/        # Search functionality
        │   ├── tournament/    # Tournament components
        │   └── ui/           # UI components (buttons, cards, etc.)
        │
        ├── lib/              # Utilities & configurations
        │   ├── mock-data.ts  # Mock data for development
        │   ├── query-provider.tsx  # React Query setup
        │   └── utils.ts      # Utility functions
        │
        ├── services/         # API services
        │   └── api.js
        │
        ├── styles/           # CSS styles
        │   └── globals.css
        │
        ├── types/            # TypeScript type definitions
        │   └── index.ts
        │
        └── utils/            # Utility functions
            └── formatters.js
```

## 🔧 Key Features

### Current Implementation
- **Search Functionality**: Search wrestlers, schools, coaches, and tournaments
- **Browse Interface**: Categorized browsing with filters
- **Tournament Brackets**: Interactive bracket displays
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Type Safety**: Full TypeScript implementation
- **Database Integration**: Supabase PostgreSQL with async connections

### API Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /api/wrestlers` - Wrestler data and search
- `GET /api/schools` - School information
- `GET /api/tournaments` - Tournament data and brackets
- `GET /api/search` - Global search functionality

### Data Models
- **Wrestler**: Profile, stats, school affiliation, weight class
- **School**: Institution info, conference, coach details
- **Coach**: Coaching staff information and history
- **Tournament**: Event details, brackets, match results
- **Match/Bracket**: Competition structure and results

## 🛠️ Development Tools

### Backend
- **FastAPI**: Modern, fast API framework
- **Uvicorn**: ASGI server for development
- **Alembic**: Database migration management
- **Asyncpg**: High-performance PostgreSQL adapter
- **Pydantic**: Data validation and settings management
- **Python-Jose**: JWT token handling

### Frontend
- **Next.js**: React framework with App Router
- **TanStack Query**: Server state management
- **Zustand**: Client state management
- **Tailwind CSS**: Utility-first CSS framework
- **TypeScript**: Static type checking
- **ESLint**: Code linting and formatting

## 🚢 Deployment

### Railway (Recommended)
The project is configured for Railway deployment with:
- `railway.json` configuration
- Docker support
- Environment variable management
- Automatic deployments from Git

### Manual Deployment
1. **Backend**: Deploy FastAPI app with Uvicorn
2. **Frontend**: Build and deploy Next.js static export
3. **Database**: Use Supabase hosted PostgreSQL

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions and support:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs` when running locally
- Review the database schema in `SUPABASE_SCHEMA.md`

---

**Note**: This project is actively developed and the structure may evolve. Always refer to the latest README and documentation for current setup instructions.