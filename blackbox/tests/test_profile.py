import pytest

def test_profile_get_success(user_session, base_url, valid_user_id):
    """GET /profile returns user profile."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/profile")
    assert resp.status_code == 200
    data = resp.json()
    assert "name" in data
    assert "phone" in data

def test_profile_missing_user_id(base_url, admin_session):
    """Missing X-User-ID should return 400."""
    resp = admin_session.get(f"{base_url}/profile")
    assert resp.status_code == 400

def test_profile_update_success(user_session, base_url, valid_user_id):
    """Valid profile update should succeed."""
    session = user_session(valid_user_id)
    payload = {"name": "New Name", "phone": "1234567890"}
    resp = session.put(f"{base_url}/profile", json=payload)
    if resp.status_code != 200:
        pytest.fail(f"Bug found: Expected 200, got {resp.status_code}")

def test_profile_update_invalid_name_short(user_session, base_url, valid_user_id):
    """Name length < 2 should return 400."""
    session = user_session(valid_user_id)
    payload = {"name": "A", "phone": "1234567890"}
    resp = session.put(f"{base_url}/profile", json=payload)
    if resp.status_code != 400:
        pytest.fail(f"Bug found: Expected 400 for short name, got {resp.status_code}")

def test_profile_update_invalid_name_long(user_session, base_url, valid_user_id):
    """Name length > 50 should return 400."""
    session = user_session(valid_user_id)
    payload = {"name": "A" * 51, "phone": "1234567890"}
    resp = session.put(f"{base_url}/profile", json=payload)
    if resp.status_code != 400:
        pytest.fail(f"Bug found: Expected 400 for long name, got {resp.status_code}")

def test_profile_update_invalid_phone(user_session, base_url, valid_user_id):
    """Phone not exactly 10 digits should return 400."""
    session = user_session(valid_user_id)
    payload = {"name": "Alice", "phone": "12345"}
    resp = session.put(f"{base_url}/profile", json=payload)
    if resp.status_code != 400:
        pytest.fail(f"Bug found: Expected 400 for invalid phone, got {resp.status_code}")
