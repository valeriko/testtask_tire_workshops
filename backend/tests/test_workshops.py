import datetime

from app.models import Workshop


NONEXISTENT_ID_WORKSHOP = 99999999

new_workshop_data = {
        "name": "New Workshop",
        "city": "New City",
        "address": "456 New St",
        "vehicle_types": "Car",
        "url_available_times": "https://example.com/available/{date_from}/{date_to}",
        "response_type": "JSON_id",
        "url_booking": "https://example.com/book/{id}",
        "booking_http_method": "POST",
        "booking_body": "{contact_info}"
    }


def test_get_filters(client, sample_workshop):
    """Test getting filter values with a sample workshop in the database"""
    response = client.get("/api/workshops/filters")
    assert response.status_code == 200

    data = response.json()
    assert "vehicle_types" in data
    assert "cities" in data
    assert "workshop_names" in data
    assert "default_date_from" in data
    assert "default_date_to" in data

    assert "Sample City" in data["cities"]
    assert "Sample Workshop" in data["workshop_names"]

    today = datetime.date.today()
    assert data["default_date_from"] == today.isoformat()
    date_to = datetime.datetime.strptime(data["default_date_to"], "%Y-%m-%d").date()
    assert date_to > today


def test_list_workshops(client, sample_workshop):
    """Test listing all workshops"""
    response = client.get("/api/workshops/")
    assert response.status_code == 200

    workshops = response.json()
    assert len(workshops) > 0
    assert workshops[0]["name"] == "Sample Workshop"
    assert workshops[0]["city"] == "Sample City"
    assert workshops[0]["vehicle_types"] == "Car,Truck"


def test_add_workshop(client):
    """Test adding a new workshop"""
    response = client.post("/api/workshops/", json=new_workshop_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "New Workshop"
    assert data["city"] == "New City"
    assert data["is_active"]
    assert "id_workshop" in data


def test_add_workshop_with_missing_data(client):
    """Test adding a workshop with missing data"""
    invalid_data = {
        "name": "Invalid Workshop",
        # Missing required fields
    }
    response = client.post("/api/workshops/", json=invalid_data)
    assert response.status_code == 500


def test_add_workshop_with_invalid_vehicle_type(client):
    """Test adding a workshop with invalid data"""
    invalid_data = new_workshop_data | {
        "vehicle_types": "Scooter",
    }
    response = client.post("/api/workshops/", json=invalid_data)
    assert response.status_code == 400


def test_add_workshop_with_invalid_booking_http_method(client):
    """Test adding a workshop with invalid data"""
    invalid_data = new_workshop_data | {
        "booking_http_method": "DELETE",
    }
    response = client.post("/api/workshops/", json=invalid_data)
    assert response.status_code == 400


def test_add_workshop_with_invalid_response_type(client):
    """Test adding a workshop with invalid data"""
    invalid_data = new_workshop_data | {
        "response_type": "CSV",
    }
    response = client.post("/api/workshops/", json=invalid_data)
    assert response.status_code == 400


def test_update_workshop(client, sample_workshop):
    """Test updating an existing workshop"""
    update_data = {
        "name": "Updated Workshop",
        "city": "Updated City",
        "vehicle_types": "Truck"
    }

    response = client.put(f"/api/workshops/{sample_workshop.id_workshop}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Updated Workshop"
    assert data["city"] == "Updated City"
    assert data["vehicle_types"] == "Truck"
    assert data["id_workshop"] == sample_workshop.id_workshop


def test_update_workshop_invalid_vehicle_type(client, sample_workshop):
    """Test updating an existing workshop with invalid data"""
    update_data = {
        "vehicle_types": "Bicycle"
    }
    response = client.put(f"/api/workshops/{sample_workshop.id_workshop}", json=update_data)
    assert response.status_code == 400


def test_update_workshop_invalid_booking_http_method(client, sample_workshop):
    """Test updating an existing workshop with invalid data"""
    update_data = {
        "booking_http_method": "GET"
    }
    response = client.put(f"/api/workshops/{sample_workshop.id_workshop}", json=update_data)
    assert response.status_code == 400


def test_update_workshop_invalid_response_type(client, sample_workshop):
    """Test updating an existing workshop with invalid data"""
    update_data = {
        "response_type": "TSV"
    }
    response = client.put(f"/api/workshops/{sample_workshop.id_workshop}", json=update_data)
    assert response.status_code == 400


def test_update_nonexistent_workshop(client):
    """Test updating a workshop that doesn't exist"""
    update_data = {"name": "Should Not Update"}

    response = client.put(f"/api/workshops/{NONEXISTENT_ID_WORKSHOP}", json=update_data)
    assert response.status_code == 400


def test_toggle_workshop_status(client, sample_workshop):
    """Test toggling workshop active status"""
    assert sample_workshop.is_active

    response = client.post(f"/api/workshops/{sample_workshop.id_workshop}/toggle-active")
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert not data["is_active"]

    response = client.post(f"/api/workshops/{sample_workshop.id_workshop}/toggle-active")
    assert response.status_code == 200
    data = response.json()
    assert data["success"]
    assert data["is_active"]


def test_toggle_nonexistent_workshop(client):
    """Test toggling status of a workshop that doesn't exist"""
    response = client.post(f"/api/workshops/{NONEXISTENT_ID_WORKSHOP}/toggle-active")
    assert response.status_code == 400


def test_filter_values_no_workshops(client):
    """Test getting filter values when no workshops exist"""
    response = client.get("/api/workshops/filters")
    assert response.status_code == 200

    data = response.json()
    assert len(data["cities"]) == 0
    assert len(data["workshop_names"]) == 0
    assert "vehicle_types" in data
    assert "default_date_from" in data
    assert "default_date_to" in data


def test_multiple_workshops_filter_values(client, db_session):
    """Test filter values with multiple workshops"""
    workshops_data = [
        Workshop(
            name="Workshop A",
            city="City A",
            address="Address A",
            vehicle_types="Car",
            url_available_times="http://testserver/a",
            response_type="JSON_id",
            url_booking="http://testserver/book/a",
            booking_http_method="POST",
            booking_body="{contact_info}",
            is_active=True
        ),
        Workshop(
            name="Workshop B",
            city="City B",
            address="Address B",
            vehicle_types="Truck",
            url_available_times="http://testserver/b",
            response_type="JSON_id",
            url_booking="http://testserver/book/b",
            booking_http_method="POST",
            booking_body="{contact_info}",
            is_active=True
        )
    ]

    for workshop in workshops_data:
        db_session.add(workshop)
    db_session.commit()

    response = client.get("/api/workshops/filters")
    assert response.status_code == 200

    data = response.json()
    assert "City A" in data["cities"]
    assert "City B" in data["cities"]
    assert "Workshop A" in data["workshop_names"]
    assert "Workshop B" in data["workshop_names"]
    assert len(data["cities"]) == 2
    assert len(data["workshop_names"]) == 2
