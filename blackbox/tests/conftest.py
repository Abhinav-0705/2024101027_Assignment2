import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"
ROLL_NUMBER = "2024101027"

def get_base_session():
    session = requests.Session()
    session.headers.update({
        "X-Roll-Number": ROLL_NUMBER,
        "Content-Type": "application/json"
    })
    return session

@pytest.fixture(scope="session")
def admin_session():
    """Session for admin endpoints (no X-User-ID needed)."""
    return get_base_session()

@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for the API."""
    return BASE_URL

@pytest.fixture(scope="function")
def user_session():
    """Factory to create a session for a given user ID."""
    def _create_session(user_id):
        session = get_base_session()
        session.headers.update({"X-User-ID": str(user_id)})
        return session
    return _create_session

@pytest.fixture(scope="session")
def valid_user_id(admin_session, base_url):
    """Retrieve a valid user ID dynamically to be used in other tests."""
    response = admin_session.get(f"{base_url}/admin/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) > 0, "No users found in the database"
    return users[0]["user_id"]
