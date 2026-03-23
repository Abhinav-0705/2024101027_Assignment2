import pytest
import requests

def test_admin_users_success(admin_session, base_url):
    """Admin endpoint to get users with valid Roll Number."""
    response = admin_session.get(f"{base_url}/admin/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        for user in data:
            assert "user_id" in user
            assert "wallet_balance" in user
            assert "loyalty_points" in user

def test_admin_missing_roll_number(base_url):
    """Missing X-Roll-Number header should return 401."""
    response = requests.get(f"{base_url}/admin/users")
    assert response.status_code == 401

def test_admin_invalid_roll_number(base_url):
    """Invalid X-Roll-Number header (text) should return 400."""
    response = requests.get(f"{base_url}/admin/users", headers={"X-Roll-Number": "invalid_roll"})
    assert response.status_code == 400

def test_admin_users_specific(admin_session, base_url, valid_user_id):
    """Admin endpoint to get specific user."""
    response = admin_session.get(f"{base_url}/admin/users/{valid_user_id}")
    assert response.status_code == 200
    user = response.json()
    assert user["user_id"] == valid_user_id

def test_admin_carts(admin_session, base_url):
    """Admin endpoint to get all carts."""
    response = admin_session.get(f"{base_url}/admin/carts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_orders(admin_session, base_url):
    """Admin endpoint to get all orders."""
    response = admin_session.get(f"{base_url}/admin/orders")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_products(admin_session, base_url):
    """Admin endpoint to get all products including inactive."""
    response = admin_session.get(f"{base_url}/admin/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_coupons(admin_session, base_url):
    """Admin endpoint to get all coupons."""
    response = admin_session.get(f"{base_url}/admin/coupons")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_tickets(admin_session, base_url):
    """Admin endpoint to get all support tickets."""
    response = admin_session.get(f"{base_url}/admin/tickets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_addresses(admin_session, base_url):
    """Admin endpoint to get all addresses."""
    response = admin_session.get(f"{base_url}/admin/addresses")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
