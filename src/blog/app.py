import asyncio

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from . import api
from .database import database
from .database import Base, engine


#
# Base.metadata.create_all(engine)
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# asyncio.run(init_models())
# print("Done")

app.include_router(api.router)
app.mount("/static", StaticFiles(directory="src/blog/static"), name="static")
