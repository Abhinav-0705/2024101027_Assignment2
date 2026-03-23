import pytest

def test_products_list_active_only(user_session, base_url, valid_user_id, admin_session):
    """GET /products should only return active products."""
    # First get all products from admin to know if there are inactive ones
    admin_prods = admin_session.get(f"{base_url}/admin/products").json()
    inactive_prods = [p for p in admin_prods if not p.get("is_active", True)]
    
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/products")
    if resp.status_code != 200:
        pytest.fail(f"Bug: Expected 200, got {resp.status_code}")
    user_prods = resp.json()
    
    for p in user_prods:
        if not p.get("is_active", True):
            pytest.fail("Bug: Inactive product returned in user list")

def test_products_get_by_id_not_found(user_session, base_url, valid_user_id):
    """Lookup for non-existent product returns 404."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/products/9999999")
    if resp.status_code != 404:
        pytest.fail(f"Bug: Expected 404 for missing product, got {resp.status_code}")

def test_products_get_exact_price(user_session, base_url, valid_user_id, admin_session):
    """Price shown must be the exact real price stored in the database."""
    admin_prods = admin_session.get(f"{base_url}/admin/products").json()
    if not admin_prods:
        return
    prod_id = admin_prods[0]["product_id"]
    expected_price = admin_prods[0]["price"]
    
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/products/{prod_id}")
    data = resp.json()
    
    if "data" in data:
        data = data["data"] # Handle varying API response structure just in case
        
    actual_price = data.get("price")
    if actual_price != expected_price:
        pytest.fail(f"Bug: Exact actual price not shown. Expected {expected_price}, got {actual_price}")

def test_products_filter_by_category(user_session, base_url, valid_user_id):
    """Filter by category must only return products matching the category."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/products?category=Electronics")
    data = resp.json()
    for prod in data:
        if prod.get("category") != "Electronics":
            pytest.fail(f"Bug: Filter returned wrong category: {prod.get('category')}")

def test_products_search_by_name(user_session, base_url, valid_user_id):
    """Search by name."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/products?search=Phone")
    data = resp.json()
    for prod in data:
        if "Phone" not in prod.get("name", ""):
            pytest.fail(f"Bug: Search returned unmatching product: {prod.get('name')}")

def test_products_sort_by_price_asc(user_session, base_url, valid_user_id):
    """Sort by price ascending."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/products?sort=price_asc")
    data = resp.json()
    prices = [p["price"] for p in data]
    if prices != sorted(prices):
        pytest.fail("Bug: Products not sorted correctly ascending")

def test_products_sort_by_price_desc(user_session, base_url, valid_user_id):
    """Sort by price descending."""
    session = user_session(valid_user_id)
    resp = session.get(f"{base_url}/products?sort=price_desc")
    data = resp.json()
    prices = [p["price"] for p in data]
    if prices != sorted(prices, reverse=True):
        pytest.fail("Bug: Products not sorted correctly descending")
