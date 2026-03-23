import pytest

@pytest.fixture
def clean_address(user_session, base_url, valid_user_id):
    """Add a temporary address for testing, and yield its ID."""
    session = user_session(valid_user_id)
    payload = {
        "label": "HOME",
        "street": "123 Main St",
        "city": "Hyderabad",
        "pincode": "500032",
        "is_default": False
    }
    resp = session.post(f"{base_url}/addresses", json=payload)
    data = resp.json()
    addr_id = data.get("address", data).get("address_id")
    yield addr_id
    # Teardown: delete it if it still exists
    session.delete(f"{base_url}/addresses/{addr_id}")

def test_addresses_get(user_session, base_url, valid_user_id):
    """GET /addresses returns a list."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/addresses")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_addresses_post_valid(user_session, base_url, valid_user_id):
    """Add a valid address."""
    session = user_session(valid_user_id)
    payload = {
        "label": "OFFICE",
        "street": "456 Tech Park",
        "city": "Bangalore",
        "pincode": "560001",
        "is_default": False
    }
    resp = session.post(f"{base_url}/addresses", json=payload)
    if resp.status_code != 201 and resp.status_code != 200:
        pytest.fail(f"Bug: Expected success status, got {resp.status_code}")
    data = resp.json()
    addr_data = data.get("address", data)
    assert "address_id" in addr_data
    assert addr_data["label"] == "OFFICE"
    
    # Clean up
    session.delete(f"{base_url}/addresses/{addr_data['address_id']}")

def test_addresses_post_invalid_label(user_session, base_url, valid_user_id):
    """Label must be HOME, OFFICE, or OTHER."""
    session = user_session(valid_user_id)
    payload = {"label": "INVALID", "street": "456 Tech Park", "city": "Bangalore", "pincode": "560001"}
    resp = session.post(f"{base_url}/addresses", json=payload)
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for invalid label, got {resp.status_code}")

def test_addresses_post_invalid_street(user_session, base_url, valid_user_id):
    """Street must be 5-100 characters."""
    session = user_session(valid_user_id)
    payload = {"label": "HOME", "street": "123", "city": "Bangalore", "pincode": "560001"}
    resp = session.post(f"{base_url}/addresses", json=payload)
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for short street, got {resp.status_code}")

def test_addresses_post_invalid_pincode(user_session, base_url, valid_user_id):
    """Pincode must be exactly 6 digits."""
    session = user_session(valid_user_id)
    payload = {"label": "HOME", "street": "456 Tech Park", "city": "Bangalore", "pincode": "123"}
    resp = session.post(f"{base_url}/addresses", json=payload)
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for invalid pincode, got {resp.status_code}")

def test_addresses_update_allowed_fields(user_session, base_url, valid_user_id, clean_address):
    """Update allows only street and is_default to change. Others should remain unchanged."""
    session = user_session(valid_user_id)
    addr_id = clean_address
    payload = {
        "label": "OTHER", # Should be ignored
        "street": "789 New Street",
        "city": "Mumbai", # Should be ignored
        "pincode": "400001", # Should be ignored
        "is_default": True
    }
    resp = session.put(f"{base_url}/addresses/{addr_id}", json=payload)
    if resp.status_code != 200:
        pytest.fail(f"Bug: Expected 200 for update, got {resp.status_code}")
    data = resp.json()
    addr_data = data.get("address", data)
    
    # Check if the returned data is the updated one
    if addr_data.get("street") != "789 New Street":
        pytest.fail("Bug: Updated data should be returned")
    
    # Check if unallowed fields were changed
    if addr_data.get("label") == "OTHER" or addr_data.get("city") == "Mumbai" or addr_data.get("pincode") == "400001":
        pytest.fail("Bug: Server allowed updating restricted fields (label, city, pincode)")

def test_addresses_update_default_unsets_others(user_session, base_url, valid_user_id):
    """Setting a new default should unset all others."""
    session = user_session(valid_user_id)
    p1 = session.post(f"{base_url}/addresses", json={"label": "HOME", "street": "Street 1", "city": "City A", "pincode": "111111", "is_default": True}).json()
    p2 = session.post(f"{base_url}/addresses", json={"label": "OFFICE", "street": "Street 2", "city": "City B", "pincode": "222222", "is_default": True}).json()
    
    # Check all addresses
    resp = session.get(f"{base_url}/addresses")
    addresses = resp.json()
    
    default_count = sum(1 for a in addresses if a["is_default"])
    
    # Clean up
    if "address_id" in p1: session.delete(f"{base_url}/addresses/{p1['address_id']}")
    if "address_id" in p2: session.delete(f"{base_url}/addresses/{p2['address_id']}")
    
    if default_count > 1:
        pytest.fail("Bug: Multiple default addresses exist at the same time")

def test_addresses_delete_non_existent(user_session, base_url, valid_user_id):
    """Deleting non-existent address returns 404."""
    session = user_session(valid_user_id)
    resp = session.delete(f"{base_url}/addresses/9999999")
    if resp.status_code != 404:
        pytest.fail(f"Bug: Expected 404 for missing address delete, got {resp.status_code}")
