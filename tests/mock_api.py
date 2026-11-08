"""
Static mock of the scamscan API routes the scraper bot talks to.

    GET  /nodes/dispatcher/me           -> this node's id as a plaintext UUID (NODE_ID, new per process)
    GET  /dispatcher/job                -> always hands out the same job (example.com)
    POST /registry/node/upload/scrape   -> accepts the whole ScrapingResult as JSON: website_data + redirect_data
                                           (assignment_id query param optional, the client doesn't send it yet)
    POST /registry/node/upload/image    -> accepts the screenshots (multipart: full, visible)

Uploads are kept in memory in `RECEIVED` and logged, nothing is persisted.

Run it for development (from the repo root):

    litestar --app tests.mock_api:app run --reload --port 8000
    # or
    python tests/mock_api.py

and point the bot at it with API="http://127.0.0.1:8000" in your .env.
"""
import logging
import uuid
from typing import Annotated, Any

from litestar import Litestar, get, post
from litestar.datastructures import UploadFile
from litestar.enums import MediaType, RequestEncodingType
from litestar.params import Body, FromQuery, HeaderParameter, JSONBody

logger = logging.getLogger("mock_api")

# What /nodes/dispatcher/me answers; config.Config.NODE.node_id ends up with this value
NODE_ID = str(uuid.uuid4())

JOB = {
    "assignment_id": "mock-assignment-1",
    "domain": {"domain": "example", "tld": "com"},
}

# assignment_id -> uploaded payload
RECEIVED: dict[str, dict[str, Any]] = {"scrapes": {}, "images": {}}


@get("/nodes/dispatcher/me", media_type=MediaType.TEXT)
async def get_me(x_node_secret: Annotated[str | None, HeaderParameter(name="X-NODE-SECRET")] = None) -> str:
    logger.info("Node id requested (secret sent: %s)", bool(x_node_secret))
    return NODE_ID


@get("/dispatcher/job")
async def get_job(node_id: FromQuery[str | None] = None) -> dict[str, Any]:
    logger.info("Job requested by node %s", node_id)
    return JOB


@post("/registry/node/upload/scrape")
async def upload_scrape(data: JSONBody[dict[str, Any]], assignment_id: FromQuery[str | None] = None) -> dict[str, str]:
    if assignment_id is None:
        logger.warning("Scrape uploaded without assignment_id")
    website_data = data.get("website_data") or {}
    redirect_data = data.get("redirect_data") or {}
    RECEIVED["scrapes"][assignment_id or "missing-assignment-id"] = data
    logger.info("Scrape received for %s (status=%s, redirect_to=%s)",
                assignment_id, website_data.get("status"), redirect_data.get("redirect_to"))
    return {"status": "ok"}


@post("/registry/node/upload/image")
async def upload_image(
    assignment_id: FromQuery[str],
    data: Annotated[dict[str, UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)],
) -> dict[str, str]:
    RECEIVED["images"][assignment_id] = {name: await f.read() for name, f in data.items()}
    logger.info("Screenshots received for %s: %s", assignment_id, list(data))
    return {"status": "ok"}


app = Litestar(route_handlers=[get_me, get_job, upload_scrape, upload_image])


if __name__ == "__main__":
    import uvicorn

    logging.basicConfig(level=logging.INFO)
    uvicorn.run(app, host="127.0.0.1", port=8000)
