from fastapi import FastAPI
from config.db import Base, engine
from routers import user as user_routes
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import pathlib
import os
import uvicorn

basedir = pathlib.Path(__file__).parents[1]
load_dotenv(basedir / ".env")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NeoContract API"}

app.include_router(user_routes.router, tags=["Users"])

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)