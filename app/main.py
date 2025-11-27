
from fastapi import FastAPI


from app.core.config import config
from app.core.logging import setup_logging
from app.router.tool import router as tool_router

logging = setup_logging()

app = FastAPI(
  title=config.app_name,
  debug=config.debug,
  logging=logging
)

app.include_router(tool_router)


@app.get("/")
def read_root():
    logging.info("Root endpoint called")
    return {"Hello": "World"}