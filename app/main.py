from fastapi import FastAPI
from app.apis.v1 import api_router
from app.db.session import engine
from app.db.models import Base
from fastapi_pagination import add_pagination


def create_tables():
    Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Job Listing API",
        description="A RESTful API for companies to post job listings and for applicants to apply.",
        version="1.0.0",
    )
    app.include_router(api_router, prefix="/api/v1")

    @app.on_event("startup")
    async def startup_event():
        create_tables()

    add_pagination(app)
    return app


app = create_app()


@app.get("/")
def read_root():
    return {"message": "Welcome to the Job Listing API"}
