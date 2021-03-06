import logging

from fastapi import APIRouter, Depends
from fastapi.responses import ORJSONResponse
from starlette.status import HTTP_200_OK
from starlette.requests import Request

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/uptime",
    tags=["Uptime"],
    status_code=HTTP_200_OK,
)
async def uptime(request: Request) -> ORJSONResponse:
    response = {
        "message": "OK"
    }
    return ORJSONResponse(content=response)