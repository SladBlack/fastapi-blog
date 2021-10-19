from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import api
from .database import Base, engine

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(api.router)
app.mount("/static", StaticFiles(directory="src/blog/static"), name="static")
