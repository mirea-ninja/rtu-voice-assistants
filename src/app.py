import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1.routes import router as api_router
from .core.config import PROJECT_NAME, API_V1_PREFIX
from .database.database import init_db

app = FastAPI(title=PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=API_V1_PREFIX)
app.add_event_handler("startup", init_db)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        # logging.FileHandler("logs.log", mode='w', encoding='UTF-8'),
        logging.StreamHandler()
    ]
)