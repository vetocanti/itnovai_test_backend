from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)

    
def test_get_products():
    response = client.get("/products/")
    assert response.status_code == 200
    assert len(response.json()["records"]) == 10

def test_get_products_by_category():
    response = client.get("/products_category/1")
    assert response.status_code == 200
    assert len(response.json()["records"]) == 10

def test_get_categories():
    response = client.get("/categories/")
    assert response.status_code == 200
    assert len(response.json()) == 10

def test_get_product_by_name():
    response = client.get("/products_name/ADads")
    assert response.status_code == 200
    assert len(response.json()["records"]) == 0   

def test_get_product_by_id():
    response = client.get("/products_id/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Product 1"
    