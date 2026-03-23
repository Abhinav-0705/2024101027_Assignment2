import pytest

def test_reviews_post_valid(user_session, base_url, valid_user_id, admin_session):
    """POST /reviews adds a review to a product."""
    prods = admin_session.get(f"{base_url}/admin/products").json()
    p = prods[0]
    
    session = user_session(valid_user_id)
    payload = {"product_id": p["product_id"], "rating": 5, "comment": "Great!"}
    resp = session.post(f"{base_url}/reviews", json=payload)
    if resp.status_code != 200 and resp.status_code != 201:
        pytest.fail(f"Bug: Expected success for review post, got {resp.status_code}")

def test_reviews_post_invalid_rating(user_session, base_url, valid_user_id, admin_session):
    """Rating not between 1 and 5 returns 400."""
    prods = admin_session.get(f"{base_url}/admin/products").json()
    p = prods[0]
    
    session = user_session(valid_user_id)
    resp = session.post(f"{base_url}/reviews", json={"product_id": p["product_id"], "rating": 6, "comment": "Great!"})
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for rating > 5, got {resp.status_code}")
        
    resp = session.post(f"{base_url}/reviews", json={"product_id": p["product_id"], "rating": 0, "comment": "Great!"})
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for rating < 1, got {resp.status_code}")
