from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.services.json_loader import load_json_to_db
from app.routers import contents

from app.routers import contents
from app.routers import posts

app.include_router(contents.router)
app.include_router(posts.router)

Base.metadata.create_all(bind=engine)

load_json_to_db()


app = FastAPI(
    title="LocalHub API",
    version="1.0.0"
)

app.include_router(contents.router)

@app.get("/")
def root():
    return {
        "message": "LocalHub API Server"
    }