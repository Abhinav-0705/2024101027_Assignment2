import pytest

@pytest.fixture
def available_product(admin_session, base_url):
    """Finds an active product with stock > 0 for testing."""
    prods = admin_session.get(f"{base_url}/admin/products").json()
    for p in prods:
        if p.get("is_active", True) and p.get("stock_quantity", 0) > 0:
            return p
    pytest.fail("Cannot run test: No active products with stock available.")

@pytest.fixture
def empty_cart(user_session, base_url, valid_user_id):
    """Ensure the user's cart is empty before testing."""
    session = user_session(valid_user_id)
    session.delete(f"{base_url}/cart/clear")
    yield session
    session.delete(f"{base_url}/cart/clear")

def test_cart_get(empty_cart, base_url):
    """GET /cart returns empty cart."""
    resp = empty_cart.get(f"{base_url}/cart")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data

def test_cart_add_success(empty_cart, base_url, available_product):
    """Add item successfully."""
    payload = {"product_id": available_product["product_id"], "quantity": 1}
    resp = empty_cart.post(f"{base_url}/cart/add", json=payload)
    if resp.status_code != 200:
        pytest.fail(f"Bug: Expected 200 for valid cart add, got {resp.status_code}")
    
    # Check cart subtotal/total
    cart_resp = empty_cart.get(f"{base_url}/cart").json()
    if len(cart_resp["items"]) == 0:
        pytest.fail("Bug: Item was not added to cart")
        
    item = cart_resp["items"][0]
    expected_subtotal = item["quantity"] * item.get("price", available_product["price"])
    if item["subtotal"] != expected_subtotal:
        pytest.fail(f"Bug: Cart item subtotal is wrong. Expected {expected_subtotal}, got {item['subtotal']}")
    
    if cart_resp["total"] != expected_subtotal:
        pytest.fail(f"Bug: Cart total is wrong. Expected {expected_subtotal}, got {cart_resp['total']}")

def test_cart_add_zero_quantity(empty_cart, base_url, available_product):
    """Quantity must be >= 1, else 400."""
    payload = {"product_id": available_product["product_id"], "quantity": 0}
    resp = empty_cart.post(f"{base_url}/cart/add", json=payload)
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for zero quantity add, got {resp.status_code}")

def test_cart_add_negative_quantity(empty_cart, base_url, available_product):
    """Negative quantity must be rejected."""
    payload = {"product_id": available_product["product_id"], "quantity": -5}
    resp = empty_cart.post(f"{base_url}/cart/add", json=payload)
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for negative quantity add, got {resp.status_code}")

def test_cart_add_missing_product(empty_cart, base_url):
    """Missing product returns 404."""
    payload = {"product_id": 9999999, "quantity": 1}
    resp = empty_cart.post(f"{base_url}/cart/add", json=payload)
    if resp.status_code != 404:
        pytest.fail(f"Bug: Expected 404 for missing product, got {resp.status_code}")

def test_cart_add_exceeding_stock(empty_cart, base_url, available_product):
    """Quantity more than stock returns 400."""
    payload = {"product_id": available_product["product_id"], "quantity": available_product["stock_quantity"] + 1}
    resp = empty_cart.post(f"{base_url}/cart/add", json=payload)
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for exceeding stock, got {resp.status_code}")

def test_cart_add_same_product_adds_quantity(empty_cart, base_url, available_product):
    """Adding same product multiple times adds to quantity, not replaces it."""
    payload = {"product_id": available_product["product_id"], "quantity": 1}
    empty_cart.post(f"{base_url}/cart/add", json=payload)
    empty_cart.post(f"{base_url}/cart/add", json=payload)
    
    cart_resp = empty_cart.get(f"{base_url}/cart").json()
    item = cart_resp["items"][0]
    if item["quantity"] != 2:
        pytest.fail(f"Bug: Expected quantity 2 after adding 1 twice, got {item['quantity']}")

def test_cart_update_zero_quantity(empty_cart, base_url, available_product):
    """Updating with quantity less than 1 returns 400."""
    empty_cart.post(f"{base_url}/cart/add", json={"product_id": available_product["product_id"], "quantity": 1})
    payload = {"product_id": available_product["product_id"], "quantity": 0}
    resp = empty_cart.post(f"{base_url}/cart/update", json=payload)
    if resp.status_code != 400:
        pytest.fail(f"Bug: Expected 400 for update zero quantity, got {resp.status_code}")

def test_cart_remove_missing(empty_cart, base_url, available_product):
    """Removing missing item returns 404."""
    payload = {"product_id": available_product["product_id"]}
    resp = empty_cart.post(f"{base_url}/cart/remove", json=payload)
    if resp.status_code != 404:
        pytest.fail(f"Bug: Expected 404 for missing cart item removal, got {resp.status_code}")
