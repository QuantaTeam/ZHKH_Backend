import typing

import fastapi

from sarah import main


async def logger(request: fastapi.Request) -> typing.Any:
    log = main.logger.bind(
        method=request.method,
        url=request.url,
        query_params=request.query_params,
        path_params=request.path_params,
    )
    return log
