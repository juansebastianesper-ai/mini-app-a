from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_serves_converter_page():
    response = client.get("/")

    assert response.status_code == 200
    assert "Conversor de unidades" in response.text


def test_serves_frontend_assets():
    response = client.get("/static/app.js")

    assert response.status_code == 200
    assert "async function convert()" in response.text


def test_unit_catalog_includes_categories():
    response = client.get("/api/units")

    assert response.status_code == 200
    assert {"longitud", "masa", "temperatura", "volumen", "superficie", "tiempo", "velocidad"} <= response.json().keys()


def test_converts_between_metric_and_imperial_units():
    response = client.post(
        "/api/convert",
        json={"category": "longitud", "from_unit": "mi", "to_unit": "km", "value": 1},
    )

    assert response.status_code == 200
    assert response.json()["value"] == 1.609344


def test_converts_temperature():
    response = client.post(
        "/api/convert",
        json={"category": "temperatura", "from_unit": "C", "to_unit": "F", "value": 100},
    )

    assert response.status_code == 200
    assert response.json()["value"] == 212


def test_rejects_units_outside_selected_category():
    response = client.post(
        "/api/convert",
        json={"category": "longitud", "from_unit": "kg", "to_unit": "m", "value": 1},
    )

    assert response.status_code == 422


def test_rejects_non_finite_values():
    response = client.post(
        "/api/convert",
        json={"category": "longitud", "from_unit": "m", "to_unit": "km", "value": "NaN"},
    )

    assert response.status_code == 422


def test_rejects_temperature_below_absolute_zero():
    response = client.post(
        "/api/convert",
        json={"category": "temperatura", "from_unit": "C", "to_unit": "K", "value": -300},
    )

    assert response.status_code == 422
