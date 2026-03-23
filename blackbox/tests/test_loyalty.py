import pytest

def test_loyalty_get(user_session, base_url, valid_user_id):
    """GET /loyalty returns points."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/loyalty")
    assert resp.status_code == 200
    data = resp.json()
    assert "loyalty_points" in data
