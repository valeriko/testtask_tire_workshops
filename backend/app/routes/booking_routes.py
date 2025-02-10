from datetime import date

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.booking_services import fetch_available_timeslots, book_timeslot


router = APIRouter()


@router.get("/available-times", summary="Get available time slots for tire changes")
async def get_available_timeslots(
    date_from: date = Query(description="Start date (YYYY-MM-DD)"),
    date_to: date = Query(description="End date (YYYY-MM-DD)"),
    vehicle_types: str = Query(None, description="Vehicle types, separated by comma"),
    cities: str = Query(None, description="Cities, separated by comma"),
    workshop_name: str = Query(None, description="Workshop name"),
    db: Session = Depends(get_db)
):
    """
    Fetch list of available times filtered by date range, vehicle type, city, or workshop name.
    """
    try:
        timeslots = await fetch_available_timeslots(
            db,
            date_from,
            date_to,
            vehicle_types,
            cities,
            workshop_name
        )
        return timeslots

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/reserve/{id_timeslot}", summary="Book a time slot")
async def make_timeslot_booking(
    id_timeslot: str,
    id_workshop: int = Query(description="Tire workshop ID"),
    customer_phone: str = Query(description="Customer phone number"),
    db: Session = Depends(get_db)
):
    """
    Book a specific time slot by ID.
    """
    try:
        # Basic phone number validation
        stripped_phone = customer_phone.replace(" ", "").replace("-", "")
        if not stripped_phone.removeprefix("+").isdigit():
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        if len(stripped_phone) < 7 or len(stripped_phone) > 15:
            raise HTTPException(status_code=400, detail="Phone number length must be between 7 and 15 digits")

        status_code, message = await book_timeslot(db, id_timeslot, id_workshop, customer_phone)
        return {"status_code": status_code, "message": message}

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)) from e
