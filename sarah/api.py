import typing

import fastapi

from sarah import deps
from sarah.applications import api as applications_api
from sarah.anomaly import api as anomaly_api

router: fastapi.APIRouter = fastapi.APIRouter()
router.include_router(applications_api.router, prefix="/applications")
router.include_router(anomaly_api.router, prefix="/anomaly")


@router.get("/")
def read_root(log: typing.Any = fastapi.Depends(deps.logger)) -> dict[str, str]:
    log.msg("root requested")
    return {"Hello": "World"}
