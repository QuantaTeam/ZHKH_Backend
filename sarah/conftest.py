from collections import abc

import httpx
import pytest

from sarah import main


@pytest.fixture(scope="module")
async def async_client() -> abc.AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(app=main.app, base_url="http://test") as c:
        yield c
