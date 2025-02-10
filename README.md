# Aggregator of tire change workshops


## About

This is a demo application created as part of a test task using **FastAPI** and **VueJS**.

The application features:
- Viewing free time slots from various tire workshops.
- Filtering workshops based on city and supported vehicle type.
- Booking available time slots.
- Configuring listed tire workshops via a user-friendly web interface.


## How to run


Start the application using Docker Compose:
```bash
docker compose up --build
```

Once started, the application will be accessible at the following URLs:

- **Frontend**: http://localhost:8080
- **Backend API Documentation** (via Swagger UI): http://localhost:8000

To run the tests:
```bash
pytest -v
```


## Planned improvements

### High priority

1. Add **authentication** to secure access to the configuration page.
2. Implement smarter **phone number validation**.

### Low priority

1. Use a **date range picker** instead of two separate date inputs.
2. Add a **country code selector** for the phone number field.
3. Improve the workshop filters: if a city is selected in the filter, only show workshops matching the selected city.
4. Replace dropdown filters for city and workshops with **Vue-Multiselect** for better usability.
