from fastapi import APIRouter, HTTPException, Body, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.workshop_services import (
    get_workshops,
    get_filter_values,
    create_workshop,
    update_workshop,
    toggle_workshop_status
)
from app.models import SAMPLE_WORKSHOP_DATA


router = APIRouter()


@router.get("/", summary="List all configured workshops")
def list_workshops(db: Session = Depends(get_db)):
    """
    List all configured workshops and their details.
    """
    try:
        workshops = get_workshops(db, active_only=False)
        return workshops
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/filters", summary="Get available filter values")
def provide_filter_values(db: Session = Depends(get_db)):
    """
    Retrieve available filter values from the database.
    """
    try:
        return get_filter_values(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/", summary="Create new workshop")
def add_workshop(workshop_data: dict = Body(..., examples=[SAMPLE_WORKSHOP_DATA]), db: Session = Depends(get_db)):
    try:
        return create_workshop(db, workshop_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/{id_workshop}", summary="Update workshop")
def edit_workshop(id_workshop: int, workshop_data: dict = Body(..., examples=[SAMPLE_WORKSHOP_DATA]), db: Session = Depends(get_db)):
    try:
        return update_workshop(db, id_workshop, workshop_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{id_workshop}/toggle-active", summary="Toggle workshop active status")
def toggle_active(id_workshop: int, db: Session = Depends(get_db)):
    try:
        return toggle_workshop_status(db, id_workshop)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
