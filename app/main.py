
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI

from pydantic import ValidationError

from sqlalchemy.exc import OperationalError, DatabaseError

from app.core.config import config
from app.core.logging import setup_logging
from app.core.exception_handlers import (
    validation_exception_handler,
    pydantic_validation_exception_handler,
    database_exception_handler,
    resource_not_found_exception_handler
)
from app.core.errors import ResourceNotFoundError
from app.router.tool import router as tool_router

logging = setup_logging()

app = FastAPI(
  title=config.app_name,
  debug=config.debug,
  logging=logging
)

# Enregistrer les gestionnaires d'exceptions
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
app.add_exception_handler(OperationalError, database_exception_handler)
app.add_exception_handler(DatabaseError, database_exception_handler)
app.add_exception_handler(ResourceNotFoundError, resource_not_found_exception_handler)

app.include_router(tool_router)


@app.get("/")
def read_root():
    logging.info("Root endpoint called")
    return {"Hello": "World"}