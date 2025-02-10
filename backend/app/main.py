import traceback

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routes import booking_routes, workshop_routes


app = FastAPI(
    title="Tire Change Booking App",
    version="1.0.0",
    debug=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(booking_routes.router, prefix="/api/booking", tags=["Booking"])
app.include_router(workshop_routes.router, prefix="/api/workshops", tags=["Workshops"])


@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
