import pytest

def test_tickets_get(user_session, base_url, valid_user_id):
    """GET /tickets returns list."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/tickets")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_tickets_post_valid(user_session, base_url, valid_user_id):
    """POST /tickets with valid data returns 201/200."""
    session = user_session(valid_user_id)
    payload = {"subject": "Need Help", "description": "Issue with order"}
    resp = session.post(f"{base_url}/tickets", json=payload)
    if resp.status_code != 201 and resp.status_code != 200:
        pytest.fail(f"Bug: Expected success status for valid ticket, got {resp.status_code}")

def test_tickets_post_missing_fields(user_session, base_url, valid_user_id):
    """Missing fields returns 400."""
    session = user_session(valid_user_id)
    resp = session.post(f"{base_url}/tickets", json={"subject": "Need Help"})
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for missing description, got {resp.status_code}")
