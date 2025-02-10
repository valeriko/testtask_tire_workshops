import os
import json
import datetime
from dateutil.relativedelta import relativedelta

import httpx
from lxml import etree
from sqlalchemy.orm import Session

from app.config import TIMEOUT_IN_SECONDS
from app.models import TimeSlot, Workshop
from app.services.workshop_services import get_workshops


def rewrite_localhost(url):
    """
    When in docker, replace host machine links with container links.
    """
    return url.replace('//localhost', '//myhost') if os.path.exists("/.dockerenv") else url


def convert_to_datetime(timestamp_string):
    return datetime.datetime.fromisoformat(timestamp_string.replace("Z", "+00:00"))


def collect_timeslots_from_external_response(data_str, workshop, date_from, date_to):
    """
    Parse timeslots from external service response.
    """
    timeslots = []

    try:
        if workshop.response_type == "JSON_id":
            data_list = json.loads(data_str)

            for item in data_list:
                if item.get("available", True):
                    slot_datetime = convert_to_datetime(item["time"])
                    timeslots.append(TimeSlot(
                        id_workshop=workshop.id_workshop,
                        id_slot=str(item["id"]),
                        slot_datetime=slot_datetime
                    ))

        elif workshop.response_type == "XML_uuid":
            root = etree.fromstring(data_str.encode("utf-8"))
            for available_time in root.findall(".//availableTime"):
                uuid_element = available_time.find("uuid")
                time_element = available_time.find("time")
                if uuid_element is not None and time_element is not None:
                    slot_datetime = convert_to_datetime(time_element.text)
                    timeslots.append(TimeSlot(
                        id_workshop=workshop.id_workshop,
                        id_slot=uuid_element.text,
                        slot_datetime=slot_datetime
                    ))

    except Exception as e:
        print(f"Error when collecting time slots: {e}")

    # Filter by date range
    timeslots = [ts for ts in timeslots if date_from <= ts.slot_datetime.date() <= date_to]

    # Drop due times
    now = datetime.datetime.now(datetime.timezone.utc)
    timeslots = [ts for ts in timeslots if ts.slot_datetime > now]

    return timeslots


async def fetch_available_timeslots(
        db: Session,
        flt_date_from: datetime.date,
        flt_date_to: datetime.date,
        flt_vehicle_types: str = None,
        flt_cities: str = None,
        flt_workshop_name: str = None
):
    """
    Fetch available times from configured workshops.
    """
    if flt_vehicle_types:
        flt_vehicle_types = flt_vehicle_types.lower().split(",")

    if flt_cities:
        flt_cities = flt_cities.lower().split(",")

    results = []

    async with httpx.AsyncClient(timeout=TIMEOUT_IN_SECONDS) as client:
        for workshop in get_workshops(db):
            # Apply filters
            if flt_workshop_name and workshop.name.lower() != flt_workshop_name.lower():
                continue
            if flt_vehicle_types:
                workshop_vehicle_types = set(workshop.vehicle_types.lower().split(","))
                if not workshop_vehicle_types.intersection(flt_vehicle_types):
                    continue
            if flt_cities:
                if workshop.city.lower() not in flt_cities:
                    continue

            # Extend the time window by one day on both ends to ensure boundary dates remain included,
            # even for APIs that compare dates using > instead of >=.
            # Any unneeded dates will be filtered out later.
            request_params = {
                'date_from': flt_date_from - relativedelta(days=1),
                'date_to': flt_date_to + relativedelta(days=1),
            }
            url = rewrite_localhost(workshop.url_available_times).format(**request_params)

            try:
                response = await client.get(url)
                response.raise_for_status()

                if response.status_code == 200:
                    timeslots = collect_timeslots_from_external_response(
                        response.text, workshop, flt_date_from, flt_date_to
                    )
                    results.extend(timeslots)

            except Exception as e:
                print(f"Error fetching slots for workshop {workshop.name}: {e}")

    results.sort(key=lambda ts: (ts.slot_datetime, ts.id_workshop))
    return [slot.model_dump() for slot in results]  # Convert to dict for JSON response


async def book_timeslot(db: Session, id_timeslot: str, id_workshop: int, customer_phone: str):
    """
    Book a time slot via the workshop API.
    """
    workshop = db.query(Workshop).filter(
        Workshop.id_workshop == id_workshop,
        Workshop.is_active
    ).first()
    print(id_workshop, workshop.name)

    if not workshop:
        return 400, "Invalid workshop ID"

    # Basic phone number validation
    stripped_phone = customer_phone.replace(" ", "").replace("-", "")
    if not stripped_phone.replace("+", "").isdigit():
        return 400, "Invalid phone number format"
    if len(stripped_phone) < 7 or len(stripped_phone) > 15:
        return 400, "Phone number length must be between 7 and 15 digits"

    booking_url = rewrite_localhost(workshop.url_booking).format(id=id_timeslot)
    booking_http_method = workshop.booking_http_method
    booking_body = workshop.booking_body.format(contact_info=customer_phone)

    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=booking_http_method,
                url=booking_url,
                data=booking_body
            )

            if response.status_code == 200:
                return 200, "Booking successful!"
            if response.status_code == 422:
                return 422, "Unfortunately, this tire change time has already been booked."
            return response.status_code, "An error occurred while booking the time slot."

        except httpx.RequestError as exc:
            print(f"Request error during booking: {exc}")
            return 500, "Failed to connect to booking service"
        except Exception as exc:
            print(f"Unexpected error during booking: {exc}")
            return 500, "An unexpected error occurred during booking"
