import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../src")
    )
)

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.predict import router as predict_router
from api.routes.predict import load_model

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading model...")
    load_model()
    print("Model loaded successfully.")
    yield

app = FastAPI(
title="AIRay Fracture Detection API",
version="1.0.0",
lifespan=lifespan
)

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }

app.include_router(
predict_router,
prefix="/predict",
tags=["Prediction"]
)
