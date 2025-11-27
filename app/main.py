
from fastapi import FastAPI


from app.core.config import config
from app.core.logging import setup_logging

logging = setup_logging()

app = FastAPI(
  title=config.app_name,
  debug=config.debug,
  logging=logging
)


@app.get("/")
def read_root():
    logging.info("Root endpoint called")
    return {"Hello": "World"}