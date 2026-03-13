import zoneinfo
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from db import create_all_tables
from app.routers import customers, invoices, transactions, plans


app = FastAPI(lifespan=create_all_tables)

app.include_router(customers.router)
app.include_router(invoices.router)
app.include_router(transactions.router)
app.include_router(plans.router)


@app.get("/")
async def root():
    return {"message": "Hola, Santiago!"}


country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Argentina/Buenos_Aires",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima",
}


@app.get("/time/{iso_code}")
async def get_time_by_sio(iso_code: str):
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)

    if not timezone_str:
        raise HTTPException(
            status_code=404, detail=f"Código ISO {iso_code} no soportado"
        )

    try:
        tz = zoneinfo.ZoneInfo(timezone_str)
        data_time_24h = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        return {"iso": iso, "timezone": timezone_str, "time": data_time_24h}

    except zoneinfo.ZoneInfoNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Zona horaria no disponiible.",
        )
