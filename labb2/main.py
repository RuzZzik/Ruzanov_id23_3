from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.db.base import Base
from app.db.session import engine
import traceback

Base.metadata.create_all(bind=engine)

app = FastAPI()

from app.api.auth import router as auth_router
from app.api.crypto import router as crypto_router
from app.api.ws import router as ws_router

app.include_router(auth_router)
app.include_router(crypto_router)
app.include_router(ws_router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "traceback": traceback.format_exc()},
    ) 