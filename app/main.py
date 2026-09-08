from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError

from app.database import engine
from app.api import auth, courses, subscription
from app.exceptions.domain import AppException
from app.exceptions.handlers import app_exception_handler, global_exception_handler, validation_exception_handler
from app.tasks.scheduler import start_scheduler, stop_scheduler
from app.config import setup_logging

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = start_scheduler()
    logger.info("Scheduler started")

    try:
        yield
    finally:
        if scheduler:
            stop_scheduler(scheduler)
            logger.info("Application shutdown complete")
        await engine.dispose()



app = FastAPI(lifespan=lifespan)


app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(auth.router)
app.include_router(courses.router)
app.include_router(subscription.router)

