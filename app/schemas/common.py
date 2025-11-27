from enum import Enum

from pydantic import BaseModel


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class NoResultsFoundResponse(BaseModel):
    message: str = "No results found"


class NotFoundResponse(BaseModel):
    message: str = "No resource with the given id found"