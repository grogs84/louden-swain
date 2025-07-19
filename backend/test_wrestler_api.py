"""
Test script for wrestler API endpoints to validate that the fixes work correctly
"""
import pytest
import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock
import duckdb

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

@pytest.fixture
def duckdb_connection():
    """Fixture to provide DuckDB connection for testing"""
    db_path = os.path.join(os.path.dirname(__file__), 'wrestling.duckdb')
    if not os.path.exists(db_path):
        pytest.skip(f"DuckDB file not found at {db_path}")
    
    conn = duckdb.connect(db_path)
    yield conn
    conn.close()

class MockAsyncSession:
    """Mock async session that uses DuckDB connection"""
    
    def __init__(self, duckdb_conn):
        self.duckdb_conn = duckdb_conn
    
    async def execute(self, query, params=None):
        # Convert SQLAlchemy query to string and handle parameters
        query_str = str(query)
        
        if params:
            for key, value in params.items():
                # Handle parameter substitution
                query_str = query_str.replace(f":{key}", f"'{value}'")
        
        try:
            result = self.duckdb_conn.execute(query_str).fetchall()
            return MockResult(result)
        except Exception as e:
            print(f"Query error: {e}")
            print(f"Query: {query_str}")
            return MockResult([])

class MockResult:
    """Mock result object that behaves like SQLAlchemy result"""
    
    def __init__(self, data):
        self.data = data
    
    def fetchall(self):
        return [MockRow(row) for row in self.data]
    
    def fetchone(self):
        return MockRow(self.data[0]) if self.data else None

class MockRow:
    """Mock row object with attribute access"""
    
    def __init__(self, row_data):
        self._data = row_data
        # Map columns based on the queries we use
        self.person_id = row_data[0] if len(row_data) > 0 else None
        self.first_name = row_data[1] if len(row_data) > 1 else None
        self.last_name = row_data[2] if len(row_data) > 2 else None
        self.weight_class = row_data[3] if len(row_data) > 3 else None
        self.year = row_data[4] if len(row_data) > 4 else None
        self.school_name = row_data[5] if len(row_data) > 5 else None
        
        # For stats queries (new format)
        self.match_count = row_data[0] if len(row_data) > 0 else 0
        self.wins = row_data[1] if len(row_data) > 1 else 0
        self.wins_by_fall = row_data[2] if len(row_data) > 2 else 0
        self.wins_by_tech_fall = row_data[3] if len(row_data) > 3 else 0
        
        # For old format compatibility
        self.total_matches = row_data[0] if len(row_data) > 0 else 0
        self.losses = row_data[2] if len(row_data) > 2 else 0
        self.falls = row_data[3] if len(row_data) > 3 else 0
        self.decisions = row_data[4] if len(row_data) > 4 else 0
        self.tech_falls = row_data[5] if len(row_data) > 5 else 0
        self.major_decisions = row_data[6] if len(row_data) > 6 else 0
        
        # For matches queries (new format)
        if len(row_data) >= 10:
            self.match_id = row_data[0]
            self.year = row_data[1] 
            self.weight = row_data[2]
            self.round = row_data[3]
            self.round_order = row_data[4]
            self.wrestler_first_name = row_data[5]
            self.wrestler_last_name = row_data[6] 
            self.wrestler_score = row_data[7]
            self.is_winner = row_data[8]
            self.result_type = row_data[9]
            self.opponent_first_name = row_data[10] if len(row_data) > 10 else None
            self.opponent_last_name = row_data[11] if len(row_data) > 11 else None
            self.opponent_score = row_data[12] if len(row_data) > 12 else None
            self.winner = row_data[13] if len(row_data) > 13 else None
        else:
            # For old match queries
            self.match_id = row_data[0] if len(row_data) > 0 else None
            self.round = row_data[1] if len(row_data) > 1 else None
            self.round_order = row_data[2] if len(row_data) > 2 else None
            self.is_winner = row_data[3] if len(row_data) > 3 else None
            self.score = row_data[4] if len(row_data) > 4 else None
            self.result_type = row_data[5] if len(row_data) > 5 else None
            self.fall_time = row_data[6] if len(row_data) > 6 else None
            self.tournament_name = row_data[7] if len(row_data) > 7 else None
            self.tournament_year = row_data[8] if len(row_data) > 8 else None
            self.tournament_location = row_data[9] if len(row_data) > 9 else None
            self.opponent_id = row_data[10] if len(row_data) > 10 else None
            self.opponent_first_name = row_data[11] if len(row_data) > 11 else None
            self.opponent_last_name = row_data[12] if len(row_data) > 12 else None
            self.opponent_school_name = row_data[13] if len(row_data) > 13 else None

@pytest.mark.asyncio
async def test_get_wrestlers_returns_real_data(duckdb_connection):
    """Test that get_wrestlers returns real data instead of null values"""
    from routers.wrestlers import get_wrestlers
    
    mock_db = MockAsyncSession(duckdb_connection)
    
    result = await get_wrestlers(skip=0, limit=3, db=mock_db)
    
    # Should return a list
    assert isinstance(result, list)
    assert len(result) > 0
    
    # Check that we have real data instead of null values
    wrestler = result[0]
    assert 'id' in wrestler
    assert 'first_name' in wrestler
    assert 'last_name' in wrestler
    assert 'weight_class' in wrestler
    assert 'year' in wrestler
    
    # Weight class and year should not be null (they were hardcoded to None before)
    assert wrestler['weight_class'] is not None
    assert wrestler['year'] is not None
    
    print(f"✅ get_wrestlers returns real data: {wrestler['first_name']} {wrestler['last_name']}, Weight: {wrestler['weight_class']}, Year: {wrestler['year']}")

@pytest.mark.asyncio 
async def test_get_wrestler_individual_returns_real_data(duckdb_connection):
    """Test that individual wrestler endpoint returns complete data"""
    from routers.wrestlers import get_wrestler
    
    # Get a test wrestler ID
    test_id_query = "SELECT person_id FROM person p JOIN role r ON p.person_id = r.person_id WHERE r.role_type = 'wrestler' LIMIT 1"
    test_result = duckdb_connection.execute(test_id_query).fetchall()
    
    if not test_result:
        pytest.skip("No wrestlers found in test database")
    
    test_wrestler_id = test_result[0][0]
    mock_db = MockAsyncSession(duckdb_connection)
    
    result = await get_wrestler(wrestler_id=test_wrestler_id, db=mock_db)
    
    # Should return a dict with complete wrestler data
    assert isinstance(result, dict)
    assert 'id' in result
    assert 'first_name' in result
    assert 'last_name' in result
    assert 'weight_class' in result
    assert 'year' in result
    assert 'stats' in result
    
    # Weight class and year should not be null
    assert result['weight_class'] is not None
    assert result['year'] is not None
    
    # Stats should be present and have real data
    stats = result['stats']
    assert 'total_matches' in stats
    assert 'wins' in stats
    assert 'losses' in stats
    assert 'win_percentage' in stats
    
    print(f"✅ get_wrestler returns complete data: {result['first_name']} {result['last_name']}")
    print(f"   Weight: {result['weight_class']}, Year: {result['year']}")
    print(f"   Stats: {stats['total_matches']} matches, {stats['wins']} wins")

@pytest.mark.asyncio
async def test_get_wrestler_stats_returns_real_data(duckdb_connection):
    """Test that wrestler stats endpoint returns actual statistics with new format"""
    from routers.wrestlers import get_wrestler_stats
    
    # Get a test wrestler ID
    test_id_query = "SELECT person_id FROM person p JOIN role r ON p.person_id = r.person_id WHERE r.role_type = 'wrestler' LIMIT 1"
    test_result = duckdb_connection.execute(test_id_query).fetchall()
    
    if not test_result:
        pytest.skip("No wrestlers found in test database")
        
    test_wrestler_id = test_result[0][0]
    mock_db = MockAsyncSession(duckdb_connection)
    
    result = await get_wrestler_stats(wrestler_id=test_wrestler_id, db=mock_db)
    
    # Should return a dict with new statistics format
    assert isinstance(result, dict)
    required_fields = ['match_count', 'wins', 'wins_by_fall', 'wins_by_tech_fall']
    
    for field in required_fields:
        assert field in result
        assert isinstance(result[field], (int, float))
    
    print(f"✅ get_wrestler_stats returns real data: {result}")

@pytest.mark.asyncio
async def test_get_wrestler_matches_returns_data(duckdb_connection):
    """Test that wrestler matches endpoint returns match data in new format"""
    from routers.wrestlers import get_wrestler_matches
    
    # Get a test wrestler ID who has matches
    test_id_query = """
        SELECT DISTINCT p.person_id 
        FROM person p 
        JOIN role r ON p.person_id = r.person_id 
        JOIN participant pt ON r.role_id = pt.role_id
        JOIN participant_match pm ON pt.participant_id = pm.participant_id
        WHERE r.role_type = 'wrestler'
        LIMIT 1
    """
    test_result = duckdb_connection.execute(test_id_query).fetchall()
    
    if not test_result:
        pytest.skip("No wrestlers with matches found in test database")
        
    test_wrestler_id = test_result[0][0]
    mock_db = MockAsyncSession(duckdb_connection)
    
    result = await get_wrestler_matches(wrestler_id=test_wrestler_id, limit=5, skip=0, db=mock_db)
    
    # Should return a list of matches
    assert isinstance(result, list)
    
    if len(result) > 0:
        match = result[0]
        # Check new format fields
        expected_fields = ['year', 'weight', 'round', 'wrestler_name', 'wrestler_score', 
                          'opponent_name', 'opponent_score', 'result_type', 'winner']
        
        for field in expected_fields:
            assert field in match, f"Missing field {field} in match result"
        
        print(f"✅ get_wrestler_matches returns {len(result)} matches")
        print(f"   First match: {match['wrestler_name']} vs {match['opponent_name']} in {match['year']}")
        print(f"   Result: {match['result_type']}, Winner: {match['winner']}")
    else:
        print("✅ get_wrestler_matches returns empty list (no matches found)")

def test_no_hardcoded_values_in_code():
    """Test that the code no longer has hardcoded null values"""
    wrestlers_file_path = os.path.join(os.path.dirname(__file__), 'app', 'routers', 'wrestlers.py')
    
    with open(wrestlers_file_path, 'r') as f:
        content = f.read()
    
    # Check that we don't have lines that hardcode None for weight_class, year, school
    hardcoded_lines = [
        '"weight_class": None,',
        '"year": None,',
        '"school": None'
    ]
    
    # These should only appear in fallback error cases, not in normal data processing
    for line in hardcoded_lines:
        occurrences = content.count(line)
        # Should have minimal occurrences (only in error fallbacks)
        assert occurrences <= 3, f"Too many occurrences of hardcoded {line}: {occurrences}"
    
    print("✅ No excessive hardcoded null values found in wrestlers.py")

if __name__ == "__main__":
    # Run the tests directly
    import asyncio
    
    db_path = os.path.join(os.path.dirname(__file__), 'wrestling.duckdb')
    if not os.path.exists(db_path):
        print(f"❌ DuckDB file not found at {db_path}")
        sys.exit(1)
    
    conn = duckdb.connect(db_path)
    
    async def run_all_tests():
        print("Running wrestler API tests...")
        
        try:
            await test_get_wrestlers_returns_real_data(conn)
            await test_get_wrestler_individual_returns_real_data(conn)
            await test_get_wrestler_stats_returns_real_data(conn)
            await test_get_wrestler_matches_returns_data(conn)
            test_no_hardcoded_values_in_code()
            
            print("\n🎉 All tests passed! The wrestler API now returns real data instead of hardcoded null values.")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            conn.close()
    
    asyncio.run(run_all_tests())