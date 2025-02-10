from datetime import date, timedelta
from unittest.mock import patch, AsyncMock

import httpx
import pytest


def test_get_available_timeslots(client, sample_workshop):
    """Test getting available timeslots with mocked external API"""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    date_to = today + timedelta(days=7)

    external_response_data = [
        {"id": "123", "time": f"{tomorrow}T10:00:00Z", "available": True},
        {"id": "124", "time": f"{tomorrow}T11:00:00Z", "available": True}
    ]

    mock_response = httpx.Response(
        status_code=200,
        json=external_response_data,
        request=httpx.Request("GET", "http://testserver")
    )

    with patch("app.services.booking_services.httpx.AsyncClient.get",
               new_callable=AsyncMock,
               return_value=mock_response):
        params = {
            "date_from": today.isoformat(),
            "date_to": date_to.isoformat(),
        }
        response = client.get("/api/booking/available-times", params=params)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert all("id_workshop" in slot for slot in data)
        assert all("slot_datetime" in slot for slot in data)
        assert all("id_slot" in slot for slot in data)


def test_book_timeslot_success(client, sample_workshop):
    """Test successful booking of a timeslot"""
    mock_response = httpx.Response(200, json={"status": "success"})

    with patch("app.services.booking_services.httpx.AsyncClient.request",
               new_callable=AsyncMock,
               return_value=mock_response):
        params = {
            "id_workshop": sample_workshop.id_workshop,
            "customer_phone": "+1234567890"
        }
        response = client.post(
            "/api/booking/reserve/test-slot-id",
            params=params
        )
        assert response.status_code == 200
        data = response.json()
        print(data)
        assert data["status_code"] == 200
        assert "success" in data["message"].lower()


def test_book_timeslot_already_booked(client, sample_workshop):
    """Test booking attempt for an already booked timeslot"""
    mock_response = httpx.Response(422, json={"status": "already booked"})

    with patch("app.services.booking_services.httpx.AsyncClient.request",
               new_callable=AsyncMock,
               return_value=mock_response):
        params = {
            "id_workshop": sample_workshop.id_workshop,
            "customer_phone": "+1234567890"
        }
        response = client.post(
            "/api/booking/reserve/test-slot-id",
            params=params
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status_code"] == 422
        assert "already" in data["message"].lower()


@pytest.mark.parametrize("phone_number", ["+1234567890", "1234567890", "+372 5123 4567"])
def test_book_timeslot_valid_phone_numbers(client, db_session, sample_workshop, phone_number):
    """Test booking with various valid phone number formats"""
    mock_response = httpx.Response(
        status_code=200,
        json={"status": "success"},
        request=httpx.Request("POST", "http://testserver")
    )

    with patch("app.services.booking_services.httpx.AsyncClient.request",
               new_callable=AsyncMock,
               return_value=mock_response):

        params = {
            "id_workshop": sample_workshop.id_workshop,
            "customer_phone": phone_number
        }
        print(params)
        response = client.post(
            "/api/booking/reserve/test-slot-id",
            params=params
        )

        assert response.status_code == 200, f"Failed for phone number: {phone_number}"
        data = response.json()

        assert "status_code" in data, f"Missing status_code for phone: {phone_number}"
        assert "message" in data, f"Missing message for phone: {phone_number}"
        assert data["status_code"] == 200, f"Wrong status code for phone: {phone_number}"
        assert "success" in data["message"].lower(), f"Wrong message for phone: {phone_number}"


@pytest.mark.parametrize("phone_number", [
    "123",  # too short
    "12345678901234567890",  # too long
    "abcdefghijk",  # invalid characters
    "+123+456",  # multiple plus signs
])
def test_book_timeslot_invalid_phone_numbers(client, sample_workshop, phone_number):
    """Test booking attempts with invalid phone numbers"""
    params = {
        "id_workshop": sample_workshop.id_workshop,
        "customer_phone": phone_number
    }
    response = client.post(
        "/api/booking/reserve/test-slot-id",
        params=params
    )
    assert response.status_code == 400


def test_book_timeslot_external_service_error(client, sample_workshop):
    """Test handling of external service errors"""
    mock_response = httpx.Response(500, json={"status": "error"})

    with patch("app.services.booking_services.httpx.AsyncClient.request",
               new_callable=AsyncMock,
               return_value=mock_response):
        params = {
            "id_workshop": sample_workshop.id_workshop,
            "customer_phone": "+1234567890"
        }
        response = client.post(
            "/api/booking/reserve/test-slot-id",
            params=params
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status_code"] == 500
        assert "error" in data["message"].lower()
