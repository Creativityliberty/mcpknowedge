import contextlib

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.config import get_settings
from app.dependencies import get_registry
from app.mcp_server import mcp


settings = get_settings()


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    get_registry().initialize()
    async with mcp.session_manager.run():
        yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Private local-first document ingestion, semantic search and MCP access.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not settings.api_token else [settings.public_base_url],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Mcp-Session-Id"],
    expose_headers=["Mcp-Session-Id"],
)
app.include_router(router)
app.mount("/mcp", mcp.streamable_http_app())


if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.app_host, port=settings.app_port, reload=False)
