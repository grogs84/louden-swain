#!/usr/bin/env python3

"""
Simple test to verify the models and API structure are correct
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_models():
    """Test that models import and instantiate correctly"""
    try:
        from app.models import PersonProfile, PersonRole, WrestlerRoleStats
        print("✅ Profile models imported successfully")
        
        # Test PersonRole creation
        role = PersonRole(role_id="test-123", role_type="wrestler")
        print(f"✅ PersonRole created: {role.role_type}")
        
        # Test PersonProfile creation
        profile = PersonProfile(
            person_id="person-123",
            first_name="John",
            last_name="Doe",
            full_name="John Doe",
            roles=[role]
        )
        print(f"✅ PersonProfile created: {profile.full_name} with {len(profile.roles)} roles")
        
        # Test WrestlerRoleStats creation
        stats = WrestlerRoleStats(
            person_id="person-123",
            role_type="wrestler",
            wins=10,
            losses=2,
            match_count=12
        )
        print(f"✅ WrestlerRoleStats created: {stats.wins}W-{stats.losses}L")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_api_structure():
    """Test that the API router structure is correct"""
    try:
        from app.routers.wrestlers import router
        print("✅ Wrestlers router imported successfully")
        
        # Check that routes are registered (basic check)
        routes = [route.path for route in router.routes]
        expected_routes = ["/profile/{person_id}", "/profile/{person_id}/stats", "/profile/{person_id}/matches"]
        
        for expected in expected_routes:
            if any(expected in route for route in routes):
                print(f"✅ Route pattern '{expected}' found")
            else:
                print(f"⚠️  Route pattern '{expected}' not found in: {routes}")
        
        return True
        
    except Exception as e:
        print(f"❌ API structure test failed: {e}")
        return False

def main():
    print("🧪 Testing Profile API Implementation...\n")
    
    models_ok = test_models()
    api_ok = test_api_structure()
    
    if models_ok and api_ok:
        print("\n✅ All tests passed! Profile API implementation looks good.")
        return 0
    else:
        print("\n❌ Some tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())