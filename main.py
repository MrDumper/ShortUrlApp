import os

import shortuuid
from fastapi import FastAPI
from pydantic import BaseModel, HttpUrl
from sqlalchemy import create_engine

from constants import DB_NAME, CONNECTION_STRING
from db_manager import DBManager
from models import Base

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    if not os.path.exists(DB_NAME):
        engine = create_engine(CONNECTION_STRING)
        Base.metadata.create_all(engine)


class LongShortUrl(BaseModel):
    long_url: HttpUrl


@app.get("/")
async def get_long_url(short_url: str):
    with DBManager() as db:
        long_url = db.get_long_by_short_url(short_url)
    return long_url


@app.post("/")
async def add_long_url(body: LongShortUrl) -> str:
    long_url = str(body.long_url)
    with DBManager() as db:
        if not db.get_long_url(long_url):
            db.create_long_url(long_url)
            id_long_url = db.get_long_url_id(long_url)
            short_url = shortuuid.random(length=5)
            db.create_short_url(short_url, id_long_url)
        else:
            db.get_short_by_long_url(long_url)
    return short_url
