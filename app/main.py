import secrets
from typing import Annotated
import zoneinfo
from datetime import datetime
import time

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from db import create_all_tables
from app.routers import customers, invoices, transactions, plans


app = FastAPI(lifespan=create_all_tables)

app.include_router(customers.router)
app.include_router(invoices.router)
app.include_router(transactions.router)
app.include_router(plans.router)


@app.middleware("http")
async def log_request_headers(request: Request, call_next):
    print(f"Headers for {request.method} {request.url.path}: {dict(request.headers)}")
    response = await call_next(request)
    return response


@app.middleware("http")
async def log_request_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"Request processed in {process_time:.2f} seconds")
    return response


def verify_credentials(credentials: HTTPBasicCredentials) -> bool:
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "password")
    return correct_username and correct_password


security = HTTPBasic()


@app.get("/")
async def root(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if not verify_credentials(credentials):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},  # necesario en 401
        )
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
