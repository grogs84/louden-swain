"""
Search API endpoints
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from ..database import Database, get_db
from ..models import (
    LegacySearchResponse,
    LegacySearchResult,
    SearchResponse,
    SearchResult,
    SearchSuggestion,
    SearchSuggestionsResponse,
    WrestlerSearchResult,
)

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_enhanced(
    q: str = Query(..., min_length=2, description="Search query"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, le=100, description="Maximum results per page"),
    type_filter: Optional[str] = Query(
        None, description="Filter by type: wrestler, school, tournament, match"
    ),
    db: Database = Depends(get_db),
):
    """Enhanced universal search with relevance scoring and pagination"""

    def calculate_relevance_score(text: str, query: str) -> float:
        """Calculate relevance score based on match quality"""
        if not text or not query:
            return 0.0

        text_lower = text.lower()
        query_lower = query.lower()

        # Exact match
        if text_lower == query_lower:
            return 1.0

        # Starts with query
        if text_lower.startswith(query_lower):
            return 0.9

        # Contains as word (word boundary match)
        import re

        if re.search(r"\b" + re.escape(query_lower) + r"\b", text_lower):
            return 0.8

        # Contains substring
        if query_lower in text_lower:
            return 0.7

        # Partial word matches
        query_words = query_lower.split()
        text_words = text_lower.split()
        matches = sum(
            1 for qw in query_words for tw in text_words if qw in tw or tw in qw
        )
        if matches > 0:
            return 0.5 + (matches / (len(query_words) + len(text_words))) * 0.2

        return 0.0

    all_results = []

    # Search wrestlers if no type filter or type is wrestler
    if not type_filter or type_filter == "wrestler":
        wrestler_query = """
        WITH wrestler_latest AS (
          SELECT DISTINCT ON (p.person_id)
            p.person_id,
            p.first_name,
            p.last_name,
            s.name as last_school,
            part.year as last_year,
            part.weight_class as last_weight_class
          FROM person p
          JOIN role r ON p.person_id = r.person_id
          JOIN participant part ON r.role_id = part.role_id
          JOIN school s ON part.school_id = s.school_id
          WHERE r.role_type = 'wrestler'
          ORDER BY p.person_id, part.year DESC
        )
        SELECT
          person_id,
          first_name,
          last_name,
          last_school,
          last_year,
          last_weight_class
        FROM wrestler_latest
        WHERE (first_name || ' ' || last_name) ILIKE $1
           OR COALESCE(first_name, '') ILIKE $1
           OR COALESCE(last_name, '') ILIKE $1
           OR COALESCE(last_school, '') ILIKE $1
        """

        wrestlers = await db.fetch_all(wrestler_query, f"%{q}%")
        for w in wrestlers:
            full_name = f"{w['first_name']} {w['last_name']}"
            subtitle = (
                f"{w['last_school']} - {w['last_weight_class']} lbs"
                if w["last_school"] and w["last_weight_class"]
                else w["last_school"]
            )

            relevance = max(
                calculate_relevance_score(full_name, q),
                calculate_relevance_score(w["first_name"], q),
                calculate_relevance_score(w["last_name"], q),
                calculate_relevance_score(w["last_school"] or "", q)
                * 0.8,  # School matches less relevant
            )

            if relevance > 0:
                all_results.append(
                    SearchResult(
                        id=str(w["person_id"]),
                        type="wrestler",
                        title=full_name,
                        subtitle=subtitle,
                        relevance_score=relevance,
                        metadata={
                            "school": w["last_school"],
                            "weight_class": w["last_weight_class"],
                            "year": w["last_year"],
                        },
                    )
                )

    # Search schools if no type filter or type is school
    if not type_filter or type_filter == "school":
        school_query = """
        SELECT
            school_id,
            name,
            location,
            mascot
        FROM school
        WHERE name ILIKE $1 OR location ILIKE $1 OR mascot ILIKE $1
        """

        schools = await db.fetch_all(school_query, f"%{q}%")
        for s in schools:
            relevance = max(
                calculate_relevance_score(s["name"], q),
                calculate_relevance_score(s["location"] or "", q) * 0.7,
                calculate_relevance_score(s["mascot"] or "", q) * 0.6,
            )

            if relevance > 0:
                all_results.append(
                    SearchResult(
                        id=str(s["school_id"]),
                        type="school",
                        title=s["name"],
                        subtitle=s["location"],
                        relevance_score=relevance,
                        metadata={"location": s["location"], "mascot": s["mascot"]},
                    )
                )

    # Search tournaments if no type filter or type is tournament
    if not type_filter or type_filter == "tournament":
        tournament_query = """
        SELECT
            tournament_id,
            name,
            year,
            location,
            date
        FROM tournament
        WHERE name ILIKE $1 OR location ILIKE $1
        ORDER BY year DESC
        """

        tournaments = await db.fetch_all(tournament_query, f"%{q}%")
        for t in tournaments:
            subtitle = (
                f"{t['year']} - {t['location']}"
                if t["year"] and t["location"]
                else str(t["year"] or t["location"] or "")
            )

            relevance = max(
                calculate_relevance_score(t["name"], q),
                calculate_relevance_score(t["location"] or "", q) * 0.7,
            )

            if relevance > 0:
                all_results.append(
                    SearchResult(
                        id=str(t["tournament_id"]),
                        type="tournament",
                        title=t["name"],
                        subtitle=subtitle,
                        relevance_score=relevance,
                        metadata={
                            "year": t["year"],
                            "location": t["location"],
                            "date": str(t["date"]) if t["date"] else None,
                        },
                    )
                )

    # Sort by relevance score (descending) then by title
    all_results.sort(key=lambda x: (-x.relevance_score, x.title))

    # Apply pagination
    total_count = len(all_results)
    paginated_results = all_results[offset : offset + limit]

    return SearchResponse(
        query=q,
        total_count=total_count,
        results=paginated_results,
        offset=offset,
        limit=limit,
    )


@router.get("/search/suggestions", response_model=SearchSuggestionsResponse)
async def search_suggestions(
    q: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(10, le=20, description="Maximum suggestions"),
    db: Database = Depends(get_db),
):
    """Get search suggestions for autocomplete"""

    suggestions = []

    # Get wrestler name suggestions
    wrestler_query = """
    SELECT DISTINCT
        p.first_name || ' ' || p.last_name as name,
        COUNT(*) as count
    FROM person p
    JOIN role r ON p.person_id = r.person_id
    WHERE r.role_type = 'wrestler'
      AND (p.first_name ILIKE $1 OR p.last_name ILIKE $1
           OR (p.first_name || ' ' || p.last_name) ILIKE $1)
    GROUP BY p.first_name, p.last_name
    ORDER BY count DESC, name
    LIMIT $2
    """

    wrestlers = await db.fetch_all(wrestler_query, f"%{q}%", limit // 2)
    for w in wrestlers:
        suggestions.append(
            SearchSuggestion(text=w["name"], type="wrestler", count=w["count"])
        )

    # Get school name suggestions
    school_query = """
    SELECT DISTINCT
        name,
        1 as count
    FROM school
    WHERE name ILIKE $1
    ORDER BY name
    LIMIT $2
    """

    schools = await db.fetch_all(school_query, f"%{q}%", limit // 2)
    for s in schools:
        suggestions.append(
            SearchSuggestion(text=s["name"], type="school", count=s["count"])
        )

    # Get tournament name suggestions
    tournament_query = """
    SELECT DISTINCT
        name,
        COUNT(*) as count
    FROM tournament
    WHERE name ILIKE $1
    GROUP BY name
    ORDER BY count DESC, name
    LIMIT $2
    """

    tournaments = await db.fetch_all(
        tournament_query, f"%{q}%", max(1, limit - len(suggestions))
    )
    for t in tournaments:
        suggestions.append(
            SearchSuggestion(text=t["name"], type="tournament", count=t["count"])
        )

    # Sort suggestions by relevance (exact matches first, then by count)
    def suggestion_relevance(suggestion):
        text_lower = suggestion.text.lower()
        query_lower = q.lower()

        if text_lower.startswith(query_lower):
            return (2, suggestion.count or 0)
        elif query_lower in text_lower:
            return (1, suggestion.count or 0)
        else:
            return (0, suggestion.count or 0)

    suggestions.sort(key=suggestion_relevance, reverse=True)

    return SearchSuggestionsResponse(query=q, suggestions=suggestions[:limit])


@router.get("/search/legacy", response_model=LegacySearchResponse)
async def search_legacy(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, le=50, description="Maximum results per category"),
    db: Database = Depends(get_db),
):
    """Legacy universal search endpoint for backward compatibility"""

    """Legacy universal search endpoint for backward compatibility"""

    # Search wrestlers
    wrestler_query = """
    SELECT DISTINCT
        p.person_id as id,
        p.first_name || ' ' || p.last_name as name,
        s.name as additional_info
    FROM person p
    JOIN role r ON p.person_id = r.person_id
    LEFT JOIN participant pt ON r.role_id = pt.role_id
    LEFT JOIN school s ON pt.school_id = s.school_id
    WHERE r.role_type = 'wrestler'
      AND (p.first_name ILIKE $1 OR p.last_name ILIKE $1
           OR (p.first_name || ' ' || p.last_name) ILIKE $1)
    ORDER BY name
    LIMIT $2
    """

    wrestlers = await db.fetch_all(wrestler_query, f"%{q}%", limit)
    wrestler_results = [
        LegacySearchResult(
            type="wrestler",
            id=w["id"],
            name=w["name"],
            additional_info=w["additional_info"],
        )
        for w in wrestlers
    ]

    # Search schools
    school_query = """
    SELECT
        school_id as id,
        name,
        location as additional_info
    FROM school
    WHERE name ILIKE $1 OR location ILIKE $1
    ORDER BY name
    LIMIT $2
    """

    schools = await db.fetch_all(school_query, f"%{q}%", limit)
    school_results = [
        LegacySearchResult(
            type="school",
            id=s["id"],
            name=s["name"],
            additional_info=s["additional_info"],
        )
        for s in schools
    ]

    # Search tournaments
    tournament_query = """
    SELECT
        tournament_id as id,
        name,
        year::text || ' - ' || location as additional_info
    FROM tournament
    WHERE name ILIKE $1
    ORDER BY year DESC, name
    LIMIT $2
    """

    tournaments = await db.fetch_all(tournament_query, f"%{q}%", limit)
    tournament_results = [
        LegacySearchResult(
            type="tournament",
            id=t["id"],
            name=t["name"],
            additional_info=t["additional_info"],
        )
        for t in tournaments
    ]

    return LegacySearchResponse(
        query=q,
        wrestlers=wrestler_results,
        schools=school_results,
        tournaments=tournament_results,
    )


@router.get("/search/wrestlers", response_model=List[WrestlerSearchResult])
async def search_wrestlers(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, le=50, description="Maximum results"),
    school: Optional[str] = Query(None, description="Filter by school"),
    weight_class: Optional[str] = Query(None, description="Filter by weight class"),
    division: Optional[str] = Query(None, description="Filter by division (D1, D2, D3)"),
    db: Database = Depends(get_db),
):
    """Search wrestlers with disambiguation hints and advanced filtering"""
    query = """
    WITH wrestler_latest AS (
      SELECT DISTINCT ON (p.person_id)
        p.person_id,
        p.first_name,
        p.last_name,
        s.name as last_school,
        s.school_type as division,
        part.year as last_year,
        part.weight_class as last_weight_class
      FROM person p
      JOIN role r ON p.person_id = r.person_id
      JOIN participant part ON r.role_id = part.role_id
      JOIN school s ON part.school_id = s.school_id
      WHERE r.role_type = 'wrestler'
      ORDER BY p.person_id, part.year DESC
    )
    SELECT
      person_id,
      first_name,
      last_name,
      last_school,
      division,
      last_year,
      last_weight_class
    FROM wrestler_latest
    WHERE (first_name || ' ' || last_name) ILIKE $1
       OR COALESCE(first_name, '') ILIKE $1
       OR COALESCE(last_name, '') ILIKE $1
    """
    
    params = [f"%{q}%"]
    
    if school:
        query += " AND COALESCE(last_school, '') ILIKE $" + str(len(params) + 1)
        params.append(f"%{school}%")
        
    if weight_class:
        query += " AND last_weight_class = $" + str(len(params) + 1)
        params.append(weight_class)
        
    if division:
        query += " AND COALESCE(division, '') ILIKE $" + str(len(params) + 1)
        params.append(f"%{division}%")
    
    query += " ORDER BY last_name, first_name LIMIT $" + str(len(params) + 1)
    params.append(limit)

    wrestlers = await db.fetch_all(query, *params)
    return [
        WrestlerSearchResult(
            person_id=w["person_id"],
            first_name=w["first_name"],
            last_name=w["last_name"],
            last_school=w["last_school"],
            last_year=w["last_year"],
            last_weight_class=w["last_weight_class"],
        )
        for w in wrestlers
    ]


@router.get("/search/schools", response_model=List[LegacySearchResult])
async def search_schools(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(20, le=100, description="Maximum results"),
    db: Database = Depends(get_db),
):
    """Search schools specifically"""
    query = """
    SELECT
        school_id as id,
        name,
        location as additional_info
    FROM school
    WHERE name ILIKE $1 OR location ILIKE $1
    ORDER BY name
    LIMIT $2
    """

    schools = await db.fetch_all(query, f"%{q}%", limit)
    return [
        LegacySearchResult(
            type="school",
            id=s["id"],
            name=s["name"],
            additional_info=s["additional_info"],
        )
        for s in schools
    ]


@router.get("/search/test-db", response_model=dict)
async def test_database_connection(db: Database = Depends(get_db)):
    """Test database connectivity and show sample data"""
    try:
        # Test connection
        query = "SELECT COUNT(*) as total FROM person"
        result = await db.fetch_one(query)

        # Get a few sample persons
        sample_query = "SELECT person_id, first_name, last_name FROM person LIMIT 3"
        samples = await db.fetch_all(sample_query)

        return {
            "status": "connected",
            "total_people": result["total"] if result else 0,
            "sample_people": samples,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/search/debug-wrestlers", response_model=dict)
async def debug_wrestlers(db: Database = Depends(get_db)):
    """Debug wrestler data structure"""
    try:
        # Check total people
        people_count = await db.fetch_one("SELECT COUNT(*) as total FROM person")

        # Check roles
        role_count = await db.fetch_one("SELECT COUNT(*) as total FROM role")
        wrestler_count = await db.fetch_one(
            "SELECT COUNT(*) as total FROM role WHERE role_type = 'wrestler'"
        )

        # Check participants
        participant_count = await db.fetch_one(
            "SELECT COUNT(*) as total FROM participant"
        )

        # Get sample wrestler with their info
        sample_wrestler = await db.fetch_one(
            """
            SELECT
                p.person_id,
                p.first_name,
                p.last_name,
                r.role_type,
                part.year,
                part.weight_class,
                s.name as school_name
            FROM person p
            JOIN role r ON p.person_id = r.person_id
            LEFT JOIN participant part ON r.role_id = part.role_id
            LEFT JOIN school s ON part.school_id = s.school_id
            WHERE r.role_type = 'wrestler'
            LIMIT 1
        """
        )

        return {
            "total_people": people_count["total"] if people_count else 0,
            "total_roles": role_count["total"] if role_count else 0,
            "total_wrestlers": wrestler_count["total"] if wrestler_count else 0,
            "total_participants": participant_count["total"]
            if participant_count
            else 0,
            "sample_wrestler": sample_wrestler,
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@router.get("/search/mock", response_model=SearchResponse)
async def search_mock(
    q: str = Query(..., min_length=2, description="Search query"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    limit: int = Query(20, le=100, description="Maximum results per page"),
    type_filter: Optional[str] = Query(
        None, description="Filter by type: wrestler, school, tournament, match"
    ),
):
    """Mock search endpoint for testing without database"""

    # Mock data for demonstration
    mock_wrestlers = [
        {
            "id": "1",
            "type": "wrestler",
            "title": "Spencer Lee",
            "subtitle": "Iowa - 125 lbs",
            "relevance_score": 0.95,
            "metadata": {
                "school": "Iowa",
                "weight_class": "125",
                "year": 2021,
                "record": "24-0",
                "ranking": 1,
            },
        },
        {
            "id": "2",
            "type": "wrestler",
            "title": "Roman Bravo-Young",
            "subtitle": "Penn State - 133 lbs",
            "relevance_score": 0.85,
            "metadata": {
                "school": "Penn State",
                "weight_class": "133",
                "year": 2021,
                "record": "23-2",
                "ranking": 2,
            },
        },
    ]

    mock_schools = [
        {
            "id": "1",
            "type": "school",
            "title": "Iowa Hawkeyes",
            "subtitle": "Iowa City, IA",
            "relevance_score": 0.90,
            "metadata": {
                "location": "Iowa City, IA",
                "conference": "Big Ten",
                "coach": "Tom Brands",
            },
        },
        {
            "id": "2",
            "type": "school",
            "title": "Penn State Nittany Lions",
            "subtitle": "University Park, PA",
            "relevance_score": 0.80,
            "metadata": {
                "location": "University Park, PA",
                "conference": "Big Ten",
                "coach": "Cael Sanderson",
            },
        },
    ]

    mock_tournaments = [
        {
            "id": "1",
            "type": "tournament",
            "title": "NCAA Division I Wrestling Championships",
            "subtitle": "2024 - Philadelphia, PA",
            "relevance_score": 0.92,
            "metadata": {
                "year": 2024,
                "location": "Philadelphia, PA",
                "date": "2024-03-21",
            },
        },
        {
            "id": "2",
            "type": "tournament",
            "title": "Big Ten Wrestling Championships",
            "subtitle": "2024 - Minneapolis, MN",
            "relevance_score": 0.75,
            "metadata": {
                "year": 2024,
                "location": "Minneapolis, MN",
                "date": "2024-03-09",
            },
        },
    ]

    # Filter results based on query and type
    all_results = []

    if not type_filter or type_filter == "wrestler":
        for wrestler in mock_wrestlers:
            if q.lower() in wrestler["title"].lower():
                all_results.append(SearchResult(**wrestler))

    if not type_filter or type_filter == "school":
        for school in mock_schools:
            if q.lower() in school["title"].lower():
                all_results.append(SearchResult(**school))

    if not type_filter or type_filter == "tournament":
        for tournament in mock_tournaments:
            if q.lower() in tournament["title"].lower():
                all_results.append(SearchResult(**tournament))

    # Sort by relevance score
    all_results.sort(key=lambda x: x.relevance_score, reverse=True)

    # Apply pagination
    total_count = len(all_results)
    paginated_results = all_results[offset : offset + limit]

    return SearchResponse(
        query=q,
        total_count=total_count,
        results=paginated_results,
        offset=offset,
        limit=limit,
    )


@router.get("/search/suggestions/mock", response_model=SearchSuggestionsResponse)
async def search_suggestions_mock(
    q: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(10, le=20, description="Maximum suggestions"),
):
    """Mock search suggestions endpoint for testing"""

    mock_suggestions = []

    # Mock wrestler suggestions
    wrestler_names = [
        "Spencer Lee",
        "Spencer Rivera",
        "Roman Bravo-Young",
        "David Taylor",
        "Kyle Dake",
    ]
    for name in wrestler_names:
        if q.lower() in name.lower():
            mock_suggestions.append(
                SearchSuggestion(text=name, type="wrestler", count=1)
            )

    # Mock school suggestions
    school_names = ["Iowa", "Penn State", "Oklahoma State", "Ohio State", "Stanford"]
    for name in school_names:
        if q.lower() in name.lower():
            mock_suggestions.append(SearchSuggestion(text=name, type="school", count=1))

    # Mock tournament suggestions
    tournament_names = [
        "NCAA Championships",
        "Big Ten Championships",
        "Pac-12 Championships",
    ]
    for name in tournament_names:
        if q.lower() in name.lower():
            mock_suggestions.append(
                SearchSuggestion(text=name, type="tournament", count=1)
            )

    return SearchSuggestionsResponse(query=q, suggestions=mock_suggestions[:limit])


@router.get("/search/coaches", response_model=List[dict])
async def search_coaches(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, le=50, description="Maximum results"),
    school: Optional[str] = Query(None, description="Filter by school"),
    db: Database = Depends(get_db),
):
    """Search coaches with optional school filtering"""
    query = """
    WITH coach_latest AS (
      SELECT DISTINCT ON (p.person_id)
        p.person_id,
        p.first_name,
        p.last_name,
        s.name as last_school,
        part.year as last_year
      FROM person p
      JOIN role r ON p.person_id = r.person_id
      LEFT JOIN participant part ON r.role_id = part.role_id
      LEFT JOIN school s ON part.school_id = s.school_id
      WHERE r.role_type = 'coach'
      ORDER BY p.person_id, part.year DESC NULLS LAST
    )
    SELECT
      person_id,
      first_name,
      last_name,
      last_school,
      last_year
    FROM coach_latest
    WHERE (first_name || ' ' || last_name) ILIKE $1
       OR COALESCE(first_name, '') ILIKE $1
       OR COALESCE(last_name, '') ILIKE $1
    """
    
    params = [f"%{q}%"]
    
    if school:
        query += " AND COALESCE(last_school, '') ILIKE $2"
        params.append(f"%{school}%")
        
    query += """
    ORDER BY last_name, first_name
    LIMIT $""" + str(len(params) + 1)
    params.append(limit)

    coaches = await db.fetch_all(query, *params)
    return [
        {
            "person_id": c["person_id"],
            "first_name": c["first_name"],
            "last_name": c["last_name"],
            "full_name": f"{c['first_name']} {c['last_name']}",
            "last_school": c["last_school"],
            "last_year": c["last_year"],
            "type": "coach"
        }
        for c in coaches
    ]


@router.get("/search/people", response_model=List[dict])
async def search_people_simple(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(25, le=50, description="Maximum results"),
    db: Database = Depends(get_db),
):
    """Simple search in person table only (for testing during migration)"""
    query = """
    SELECT
      person_id,
      first_name,
      last_name,
      search_name,
      city_of_origin,
      state_of_origin
    FROM person
    WHERE (first_name || ' ' || last_name) ILIKE $1
       OR COALESCE(search_name, '') ILIKE $1
       OR COALESCE(first_name, '') ILIKE $1
       OR COALESCE(last_name, '') ILIKE $1
    ORDER BY last_name, first_name
    LIMIT $2
    """

    people = await db.fetch_all(query, f"%{q}%", limit)
    return [dict(person) for person in people]
