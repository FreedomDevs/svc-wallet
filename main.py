#!/usr/bin/env python3
from fastapi import FastAPI
from routes import routers
import uvicorn

app = FastAPI()

for route in routers:
    app.include_router(route)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=9006, reload=True)

