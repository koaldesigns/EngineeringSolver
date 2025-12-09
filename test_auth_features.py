"""
Comprehensive test script for authentication and user management features.
Run with: python test_auth_features.py
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_test(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details and not passed:
        print(f"       Details: {details}")

def test_health():
    """Test health endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/health")
        return r.status_code == 200 and r.json().get("status") == "ok"
    except Exception as e:
        return False

def test_root():
    """Test root endpoint"""
    try:
        r = requests.get(f"{BASE_URL}/")
        return r.status_code == 200
    except Exception as e:
        return False

def test_registration_invalid_token():
    """Test registration with invalid token fails"""
    try:
        r = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": "testuser",
            "password": "testpass",
            "token": "INVALID-TOKEN"
        })
        return r.status_code == 400 and "Invalid" in r.json().get("detail", "")
    except Exception as e:
        return False

def test_registration_valid_token():
    """Test registration with valid token succeeds"""
    try:
        r = requests.post(f"{BASE_URL}/api/auth/register", json={
            "username": f"testuser_{int(time.time())}",
            "password": "testpass123",
            "token": "ENG-7K2M9-XP4NQ"
        })
        if r.status_code == 200:
            data = r.json()
            return "access_token" in data and "user" in data
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login_invalid():
    """Test login with wrong credentials fails"""
    try:
        r = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "nonexistent",
            "password": "wrongpass"
        })
        return r.status_code == 401
    except Exception as e:
        return False

def test_custom_tabs_unauthenticated():
    """Test custom tabs returns empty when not authenticated"""
    try:
        r = requests.get(f"{BASE_URL}/api/custom-tabs")
        if r.status_code == 200:
            data = r.json()
            return data.get("tabs") == [] and data.get("logged_in") == False
        return False
    except Exception as e:
        return False

def test_save_tabs_requires_auth():
    """Test saving tabs requires authentication"""
    try:
        r = requests.post(f"{BASE_URL}/api/custom-tabs", json={
            "tabs": []
        })
        return r.status_code == 401 or r.status_code == 403
    except Exception as e:
        return False

def test_preferences_requires_auth():
    """Test preferences requires authentication"""
    try:
        r = requests.get(f"{BASE_URL}/api/preferences")
        return r.status_code == 401 or r.status_code == 403
    except Exception as e:
        return False

def test_admin_requires_auth():
    """Test admin endpoints require auth"""
    try:
        r = requests.get(f"{BASE_URL}/api/admin/users")
        return r.status_code == 401 or r.status_code == 403
    except Exception as e:
        return False

def test_full_auth_flow():
    """Test complete authentication flow"""
    unique_id = int(time.time())
    username = f"flowtest_{unique_id}"
    password = "testpass123"
    
    # Register (use a different token)
    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": username,
        "password": password,
        "token": "ENG-3H8Y6-RW2JL"
    })
    
    if r.status_code != 200:
        return False, "Registration failed"
    
    token = r.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test /me endpoint
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    if r.status_code != 200:
        return False, "/me endpoint failed"
    
    user_data = r.json()
    if user_data.get("username") != username:
        return False, "Username mismatch"
    
    # Test preferences
    r = requests.get(f"{BASE_URL}/api/preferences", headers=headers)
    if r.status_code != 200:
        return False, "Get preferences failed"
    
    # Test update preferences
    r = requests.put(f"{BASE_URL}/api/preferences", headers=headers, json={
        "theme_mode": "light",
        "accent_hue": 180
    })
    if r.status_code != 200:
        return False, "Update preferences failed"
    
    # Verify preference update
    r = requests.get(f"{BASE_URL}/api/preferences", headers=headers)
    prefs = r.json()
    if prefs.get("theme_mode") != "light" or prefs.get("accent_hue") != 180:
        return False, "Preferences not saved correctly"
    
    # Test custom tabs
    r = requests.get(f"{BASE_URL}/api/custom-tabs", headers=headers)
    if r.status_code != 200:
        return False, "Get custom tabs failed"
    
    tabs_data = r.json()
    if not tabs_data.get("logged_in"):
        return False, "Should show logged_in=True"
    
    # Test saving tabs
    test_tabs = {
        "tabs": [{
            "id": "test_tab_1",
            "name": "Test Tab",
            "icon": "📐",
            "equationSets": [{
                "id": "eq_1",
                "title": "Test Equations",
                "description": "Test description",
                "equations": "x = 5\ny = x * 2"
            }]
        }]
    }
    
    r = requests.post(f"{BASE_URL}/api/custom-tabs", headers=headers, json=test_tabs)
    if r.status_code != 200:
        return False, "Save custom tabs failed"
    
    # Verify tabs saved
    r = requests.get(f"{BASE_URL}/api/custom-tabs", headers=headers)
    saved_tabs = r.json().get("tabs", [])
    if len(saved_tabs) != 1:
        return False, "Tabs not saved correctly"
    
    if saved_tabs[0].get("name") != "Test Tab":
        return False, "Tab data mismatch"
    
    # Test token refresh
    r = requests.post(f"{BASE_URL}/api/auth/refresh", headers=headers)
    if r.status_code != 200:
        return False, "Token refresh failed"
    
    new_token = r.json().get("access_token")
    if not new_token:
        return False, "No new token returned"
    
    return True, "All flow tests passed"

def test_solve_still_works():
    """Verify the solve endpoint still works"""
    try:
        r = requests.post(f"{BASE_URL}/api/solve", json={
            "equations": ["x = 5", "y = x * 2"],
            "angle_unit": "deg"
        })
        if r.status_code == 200:
            data = r.json()
            return data.get("status") == "converged"
        return False
    except Exception as e:
        return False

def run_all_tests():
    print("=" * 60)
    print("AUTHENTICATION FEATURE TESTS")
    print("=" * 60)
    print()
    
    tests = [
        ("Health endpoint", test_health),
        ("Root endpoint", test_root),
        ("Solve endpoint (regression)", test_solve_still_works),
        ("Registration with invalid token", test_registration_invalid_token),
        ("Custom tabs without auth returns empty", test_custom_tabs_unauthenticated),
        ("Save tabs requires auth", test_save_tabs_requires_auth),
        ("Preferences requires auth", test_preferences_requires_auth),
        ("Admin endpoints require auth", test_admin_requires_auth),
        ("Login with invalid credentials", test_login_invalid),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            print_test(name, result)
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print_test(name, False, str(e))
            failed += 1
    
    print()
    print("-" * 60)
    print("FULL AUTHENTICATION FLOW TEST")
    print("-" * 60)
    
    try:
        result, details = test_full_auth_flow()
        print_test("Complete auth flow", result, details)
        if result:
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print_test("Complete auth flow", False, str(e))
        failed += 1
    
    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
