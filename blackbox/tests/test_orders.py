import pytest

def test_orders_get(user_session, base_url, valid_user_id):
    """GET /orders returns a list of orders."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/orders")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_orders_get_by_id_invalid(user_session, base_url, valid_user_id):
    """GET /orders/{invalid_id} returns 404."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/orders/999999")
    if resp.status_code != 404:
        pytest.fail(f"Bug: Expected 404 for nonexistent order, got {resp.status_code}")
