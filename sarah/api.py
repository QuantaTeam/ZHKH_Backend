import typing

import fastapi

from sarah import deps

router: fastapi.APIRouter = fastapi.APIRouter()


@router.get("/")
def read_root(log: typing.Any = fastapi.Depends(deps.logger)) -> dict[str, str]:
    log.msg("root requested")
    return {"Hello": "World"}
