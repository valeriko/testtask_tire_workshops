from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean
from pydantic import BaseModel

from app.database import Base


class Workshop(Base):
    __tablename__ = 'workshops'

    id_workshop = Column(Integer, primary_key=True, autoincrement=True)
    is_active = Column(Boolean, default=True)
    name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    address = Column(String, nullable=False)
    vehicle_types = Column(String)
    url_available_times = Column(String, nullable=False)
    response_type = Column(String, nullable=False)
    url_booking = Column(String, nullable=False)
    booking_http_method = Column(String, nullable=False)
    booking_body = Column(String, nullable=False)


class TimeSlot(BaseModel):
    id_workshop: int
    id_slot: str
    slot_datetime: datetime


SAMPLE_WORKSHOP_DATA = {
    "name": "Sample Workshop",
    "city": "Sample City",
    "address": "123 Sample St",
    "vehicle_types": "Car,Truck",
    "url_available_times": "http://workshop_api/available/{date_from}/{date_to}",
    "response_type": "JSON_id",
    "url_booking": "http://workshop_api/book/{id}",
    "booking_http_method": "POST",
    "booking_body": "{contact_info}",
}
