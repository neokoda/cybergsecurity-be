from fastapi import FastAPI
from config.db import Base, engine
from routers import auth as user_routes
from routers import compliance as compliance_routes
from routers import contract as contract_routes
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

app.include_router(user_routes.router)
app.include_router(compliance_routes.router)
app.include_router(contract_routes.router)

Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)