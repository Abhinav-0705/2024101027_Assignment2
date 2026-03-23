import pytest

def test_wallet_get(user_session, base_url, valid_user_id):
    """GET /wallet/balance returns correctly formatted balance."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/wallet/balance")
    assert resp.status_code == 200
    data = resp.json()
    assert "wallet_balance" in data
    assert isinstance(data["wallet_balance"], float) or isinstance(data["wallet_balance"], int)

def test_wallet_add_funds_valid(user_session, base_url, valid_user_id):
    """Adding valid funds to wallet."""
    session = user_session(valid_user_id)
    initial_balance = session.get(f"{base_url}/wallet/balance").json()["wallet_balance"]
    
    resp = session.post(f"{base_url}/wallet/add", json={"amount": 100})
    if resp.status_code != 200:
        pytest.fail(f"Bug: Expected 200 for adding valid funds, got {resp.status_code}")
        
    new_balance = session.get(f"{base_url}/wallet/balance").json()["wallet_balance"]
    # Due to float precision, we check math loosely
    if abs(new_balance - (initial_balance + 100.0)) > 0.01:
        pytest.fail("Bug: Wallet balance not updated correctly.")

def test_wallet_add_funds_invalid_amount(user_session, base_url, valid_user_id):
    """Adding <= 0 funds should return 400."""
    session = user_session(valid_user_id)
    resp = session.post(f"{base_url}/wallet/add", json={"amount": 0})
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for 0 amount, got {resp.status_code}")
    
    resp = session.post(f"{base_url}/wallet/add", json={"amount": -50})
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for negative amount, got {resp.status_code}")
