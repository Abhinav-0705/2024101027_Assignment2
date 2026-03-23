import pytest

def test_checkout_empty_cart(user_session, base_url, valid_user_id):
    """Checkout with empty cart returns 400."""
    session = user_session(valid_user_id)
    session.delete(f"{base_url}/cart/clear") # Ensure empty
    resp = session.post(f"{base_url}/checkout", json={"payment_method": "COD"})
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for empty cart checkout, got {resp.status_code}")

def test_checkout_invalid_method(user_session, base_url, valid_user_id):
    """Invalid payment method returns 400."""
    session = user_session(valid_user_id)
    resp = session.post(f"{base_url}/checkout", json={"payment_method": "INVALID"})
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for invalid payment method, got {resp.status_code}")
