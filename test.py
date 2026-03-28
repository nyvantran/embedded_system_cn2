import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from app.api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting FastAPI application")
    yield
    print("Stopping FastAPI application")


def create_app():
    app = FastAPI(
        title="embedded_system cn2",
        description="embedded_system cn2",
        docs_url="/docs",
        lifespan=lifespan,
    )
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()


@app.get("/")
async def root():
    html_path = "templates/index.html"
    return HTMLResponse(content=open(html_path, "rb").read())


if __name__ == "__main__":
    print("🚀 Starting High-Performance FastAPI Server")
    print("📊 Access dashboard at: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
