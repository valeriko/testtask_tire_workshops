from app.services.sanitization import sanitize_input, sanitize_data


def test_sanitize_input():
    assert sanitize_input('<script>alert("xss")</script>') == '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;'

    assert sanitize_input('Normal text 123') == 'Normal text 123'

    assert sanitize_input(None) is None


def test_sanitize_data():
    test_data = {
        'name': '<script>Bad name</script>',
        'city': 'Safe City',
        'address': '<a href=javascript:alert("bad")>',
        'vehicle_types': '"Car",Truck',
        'url_available_times': '<script>alert(1)</script>',
        'response_type': 'JSON_id',
        'booking_http_method': 'POST',
        'booking_body': '<payload>{contact_info}</payload>',
    }

    sanitized = sanitize_data(test_data)

    assert '<script>' not in sanitized['name']
    assert '<' not in sanitized['address']
    assert '"' not in sanitized['vehicle_types']
    assert '<' not in sanitized['url_available_times']
    assert '<' in sanitized['booking_body']


# Integration test with workshop services
def test_workshop_creation_with_dangerous_input(client):
    dangerous_data = {
        'name': '<script>alert("xss")</script>Workshop',
        'city': '<a href=javascript:alert("city")>a</a>',
        'address': '<script>alert(1)</script>',
        'vehicle_types': 'Car,Truck',
        'url_available_times': 'http://foo/{date_from}/{date_to}',
        'response_type': 'JSON_id',
        'url_booking': 'http://foo/book/{id}',
        'booking_http_method': 'POST',
        'booking_body': '<body>{contact_info}</body>'
    }

    response = client.post('/api/workshops/', json=dangerous_data)
    assert response.status_code == 200

    data = response.json()
    assert '<script>' not in data['name']
    assert '<' not in data['city']
    assert '<' not in data['address']
    assert '<' in data['booking_body']
