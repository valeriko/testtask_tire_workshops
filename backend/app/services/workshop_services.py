import datetime
from dateutil.relativedelta import relativedelta

from app.models import Workshop
from app.services.sanitization import sanitize_data
import app.config as app_config


def get_workshops(db, active_only=True):
    """
    Retrieves workshops from the database, optionally filtering only active ones.
    """
    query = db.query(Workshop)
    if active_only:
        query = query.filter(Workshop.is_active)

    workshops = query.all()
    return workshops


def get_default_date_range():
    today = datetime.date.today()
    return {
        'default_date_from': today,
        'default_date_to': today + relativedelta(days=app_config.DEFAULT_SEARCH_PERIOD_IN_DAYS),
    }


def get_filter_values(db):
    """
    Retrieves workshops from the database, optionally filtering only active ones.
    """
    workshops = get_workshops(db)
    cities = set(w.city for w in workshops)
    workshop_names = set(w.name for w in workshops)

    filters_data = get_default_date_range() | {
        'vehicle_types': app_config.VEHICLE_TYPES,
        'cities': sorted(cities),
        'workshop_names': sorted(workshop_names),
        'booking_http_methods': app_config.BOOKING_HTTP_METHODS,
        'response_types': app_config.RESPONSE_TYPES,
    }
    return filters_data


def check_vehicle_types(vehicle_types):
    vehicle_types = vehicle_types.lower().split(",")
    allowed_vehicle_types = set(vt.lower() for vt in app_config.VEHICLE_TYPES)
    if not all(vt in allowed_vehicle_types for vt in vehicle_types if vt):
        raise ValueError(f"Invalid vehicle types: {vehicle_types}")


def check_booking_http_method(booking_http_method):
    if booking_http_method not in app_config.BOOKING_HTTP_METHODS:
        raise ValueError(f"Invalid booking HTTP method: {booking_http_method}")


def check_response_type(response_type):
    if response_type not in app_config.RESPONSE_TYPES:
        raise ValueError(f"Invalid response type: {response_type}")


def check_values(workshop_data: dict):
    for key in workshop_data:
        workshop_data[key] = workshop_data[key].strip()

    if "vehicle_types" in workshop_data:
        check_vehicle_types(workshop_data["vehicle_types"])
    if "booking_http_method" in workshop_data:
        check_booking_http_method(workshop_data["booking_http_method"])
    if "response_type" in workshop_data:
        check_response_type(workshop_data["response_type"])


def create_workshop(db, workshop_data: dict):
    check_values(workshop_data)
    sanitized_data = sanitize_data(workshop_data) | {"is_active": True}

    workshop = Workshop(**sanitized_data)
    db.add(workshop)
    db.commit()
    db.refresh(workshop)
    return workshop


def update_workshop(db, id_workshop: int, workshop_data: dict):
    check_values(workshop_data)
    sanitized_data = sanitize_data(workshop_data)

    workshop = db.query(Workshop).filter(Workshop.id_workshop == id_workshop).first()
    if not workshop:
        raise ValueError(f"Workshop with id {id_workshop} not found")

    for key, value in sanitized_data.items():
        setattr(workshop, key, value)

    db.commit()
    db.refresh(workshop)
    return workshop


def toggle_workshop_status(db, id_workshop: int):
    workshop = db.query(Workshop).filter(Workshop.id_workshop == id_workshop).first()
    if not workshop:
        raise ValueError(f"Workshop with id {id_workshop} not found")

    workshop.is_active = not workshop.is_active
    db.commit()
    return {"success": True, "is_active": workshop.is_active}
