# 🎯 NCAA Wrestling Fan Site - Feature Roadmap & Implementation Guide

This document outlines the complete feature set for the NCAA wrestling fan site, with detailed implementation requirements for both frontend and backend. This serves as a specification for autonomous development by GitHub Copilot.

## 🏗️ Current Architecture

### Backend (FastAPI + Supabase PostgreSQL)
- **Database**: Supabase PostgreSQL with asyncpg
- **API**: FastAPI with async/await
- **Structure**: Clean router-based architecture
- **Base URL**: `http://localhost:8000/api`

### Frontend (React)
- **Framework**: React with modern hooks
- **Styling**: Modern, responsive design
- **API Client**: Single centralized service
- **Base URL**: `http://localhost:3000`

---

## 🎯 Core Features & Implementation Requirements

### 1. **Dynamic Wrestler Search** ⭐ (TOP PRIORITY)

**User Story**: As a wrestling fan, I want to search for wrestlers by name and immediately see results with disambiguation hints to find the right wrestler.

#### Frontend Implementation
**File**: `frontend/src/components/WrestlerSearch.js`
```javascript
// Required functionality:
- Debounced search input (300ms delay)
- Live results dropdown
- Results show: "Name + Last School, Year • Weight Class"
- Click result → navigate to wrestler profile
- Loading states and error handling
- Responsive design for mobile/desktop
```

**File**: `frontend/src/hooks/useWrestlerSearch.js`
```javascript
// Custom hook for search logic:
- Debounced API calls
- Search state management
- Results caching (optional)
```

#### Backend Implementation
**Status**: ✅ COMPLETE - `/api/search/wrestlers` endpoint ready

---

### 2. **Wrestler Profile Page** ⭐ (TOP PRIORITY)

**User Story**: As a wrestling fan, I want to view a wrestler's complete profile including stats, match history, and career progression.

#### Frontend Implementation
**File**: `frontend/src/pages/WrestlerProfilePage.js`
```javascript
// Required sections:
1. Header: Name, photo placeholder, basic info
2. Career Stats: W-L record, win percentage, pins, etc.
3. Tournament Results: Placements by year
4. Match History: Searchable/filterable match log
// 5. Career Timeline: Visual progression
// 6. Head-to-Head: Records vs specific opponents
```

**File**: `frontend/src/components/wrestler/`
- `WrestlerHeader.js` - Basic info display
- `CareerStats.js` - Win/loss statistics
- `MatchHistory.js` - Tabulated match results
- `TournamentResults.js` - Tournament placements
<!-- - `CareerTimeline.js` - Visual career progression -->

#### Backend Implementation
**Files to Create/Update**:
- `backend/app/routers/wrestlers.py` - Add full profile endpoints
- `backend/app/models.py` - Add detailed response models

**Required Endpoints**:
```python
GET /api/wrestlers/{wrestler_id}/profile
# Full wrestler profile with basic info

GET /api/wrestlers/{wrestler_id}/stats
# Career statistics (W-L, pins, etc.)

GET /api/wrestlers/{wrestler_id}/matches
# Match history with pagination

GET /api/wrestlers/{wrestler_id}/tournaments
# Tournament results and placements

# GET /api/wrestlers/{wrestler_id}/head-to-head/{opponent_id}
# # Head-to-head record vs specific opponent
```

---

### 3. **School Profile Pages** ⭐ (HIGH PRIORITY)

**User Story**: As a fan, I want to view school wrestling programs, their wrestlers by year, and team statistics.

#### Frontend Implementation
**File**: `frontend/src/pages/SchoolProfilePage.js`
**Components**: 
- `SchoolHeader.js` - School info, mascot, location
- `RosterByYear.js` - Wrestlers by graduation year
- `TeamStats.js` - Overall program statistics
- `SchoolHistory.js` - Notable achievements

#### Backend Implementation
**Required Endpoints**:
```python
GET /api/schools/{school_id}/profile
GET /api/schools/{school_id}/roster/{year}
GET /api/schools/{school_id}/stats
GET /api/schools/{school_id}/tournaments
```

---

### 4. **Tournament Brackets & Results** (MEDIUM PRIORITY)

**User Story**: As a fan, I want to view tournament brackets and results in an interactive format.

#### Frontend Implementation
**File**: `frontend/src/pages/TournamentPage.js`
**Components**:
- `BracketVisualization.js` - Interactive bracket display
- `TournamentResults.js` - Results by weight class
- `TournamentStats.js` - Tournament statistics

#### Backend Implementation
**Required Endpoints**:
```python
GET /api/tournaments/{tournament_id}/brackets/{weight_class}
GET /api/tournaments/{tournament_id}/results
GET /api/tournaments/{tournament_id}/matches
```

---

### 5. **Advanced Search & Filtering** (MEDIUM PRIORITY)

**User Story**: As a fan, I want to search and filter across wrestlers, schools, and tournaments with multiple criteria.

#### Frontend Implementation
**File**: `frontend/src/pages/SearchPage.js`
**Components**:
- `SearchFilters.js` - Multi-criteria search form
- `SearchResults.js` - Tabulated results with sorting
- `SavedSearches.js` - Save/load search criteria

#### Backend Implementation
**Required Endpoints**:
```python
GET /api/search/advanced
# Multi-criteria search with filters
# Supports: name, school, year range, weight class, state, etc.
```

---

### 6. **Head-to-Head Comparisons** (MEDIUM PRIORITY)

**User Story**: As a fan, I want to compare two wrestlers' careers and see their head-to-head record.

#### Frontend Implementation
**File**: `frontend/src/pages/ComparisonPage.js`
**Components**:
- `WrestlerSelector.js` - Search and select wrestlers
- `ComparisonTable.js` - Side-by-side stats
- `HeadToHeadHistory.js` - Match history between them

---

### 7. **Statistics Dashboard** (LOW PRIORITY)

**User Story**: As a fan, I want to explore interesting statistics and records across the sport.

#### Frontend Implementation
**File**: `frontend/src/pages/StatsPage.js`
**Components**:
- `RecordHolders.js` - Notable records and achievements
- `StatsTrends.js` - Charts and visualizations
- `InterestingFacts.js` - Fun facts and trivia

---

## 🔧 Technical Implementation Guidelines

### Database Migration Handling
```javascript
// All components should handle migration state gracefully
const handleMigrationState = (data, loading, error) => {
  if (loading) return <LoadingSpinner />
  if (error?.includes('relation does not exist')) {
    return <MigrationNotice />
  }
  return <ComponentContent />
}
```

### Error Boundaries
```javascript
// Implement error boundaries for all major components
<ErrorBoundary fallback={<ErrorFallback />}>
  <Component />
</ErrorBoundary>
```

### API Client Pattern
```javascript
// Use consistent API client pattern
const api = {
  wrestlers: {
    search: (query) => fetch(`/api/search/wrestlers?q=${query}`),
    profile: (id) => fetch(`/api/wrestlers/${id}/profile`),
    stats: (id) => fetch(`/api/wrestlers/${id}/stats`),
  },
  // etc.
}
```

### Responsive Design Requirements
- Mobile-first approach
- Breakpoints: 320px, 768px, 1024px, 1440px
- Touch-friendly interface elements
- Fast loading on mobile networks

---

## 📋 Implementation Checklist Templates

### For New Feature Implementation:

#### Frontend Checklist:
- [ ] Create component files in appropriate directory
- [ ] Implement responsive design
- [ ] Add loading states
- [ ] Add error handling
- [ ] Handle migration state
- [ ] Add prop-types or TypeScript
- [ ] Write basic tests (optional)
- [ ] Update navigation/routing

#### Backend Checklist:
- [ ] Create/update router endpoints
- [ ] Add Pydantic models for request/response
- [ ] Implement database queries
- [ ] Add error handling
- [ ] Add input validation
- [ ] Add pagination where needed
- [ ] Test endpoints manually
- [ ] Update API documentation

---

## 🎨 Design Principles

### Visual Design
- **Clean, modern interface** - Focus on content, minimal clutter
- **Wrestling-themed colors** - Deep reds, blues, golds
- **Typography** - Clear, readable fonts for data tables
- **Icons** - Simple, recognizable icons for actions

### User Experience
- **Fast searches** - Results appear as you type
- **Intuitive navigation** - Clear breadcrumbs and back buttons
- **Data density** - Show lots of information without overwhelming
- **Progressive disclosure** - Details expand on demand

---

## 🚀 Implementation Priority Order

### Phase 1 (MVP - Post Migration)
1. ✅ Dynamic Wrestler Search (Backend complete, Frontend needed)
2. 🔄 Wrestler Profile Page (Partial backend, Frontend needed)
3. 🔄 Basic School Profiles (Backend needed, Frontend needed)

### Phase 2 (Enhanced Features)
4. Tournament Results Display
5. Advanced Search & Filtering
6. Enhanced School Profiles

### Phase 3 (Advanced Features)
7. Head-to-Head Comparisons
8. Statistics Dashboard
9. User accounts and favorites (future)

---

## 📝 Notes for GitHub Copilot

### Context to Remember:
- This is a **wrestling fan site**, not a coaching tool
- Users are **browsing and exploring** wrestling data for entertainment
- **Performance matters** - wrestling fans want fast access to stats
- **Disambiguation is key** - many wrestlers have common names
- **Mobile usage is high** - design mobile-first

### Common Patterns:
- All API calls should handle async/await properly
- All components need loading and error states
- Search functionality should be debounced
- Data tables should be sortable and filterable
- Use consistent naming: `wrestler_id`, `school_id`, etc.

### Migration-Safe Development:
- Always check if tables exist before querying
- Provide fallbacks for missing data
- Show helpful messages during migration
- Test with both empty and populated database states

---

**Last Updated**: July 19, 2025  
**Version**: 1.0  
**Status**: Ready for autonomous development
