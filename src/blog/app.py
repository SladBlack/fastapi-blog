from fastapi import FastAPI

from . import api
# from .database import Base, engine
#
# Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(api.router)
