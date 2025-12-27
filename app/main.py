from fastapi import FastAPI
from app.api.wallets import router as wallets_router
from app.api.health import router as health_router

app = FastAPI(title="svc-wallet", version="1.0.0")

app.include_router(wallets_router)
app.include_router(health_router)
