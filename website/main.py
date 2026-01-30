from pathlib import Path

from cross_docs import CrossDocs
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from inertia import configure_inertia
from inertia.fastapi.experimental import inertia_lifespan

configure_inertia(vite_entry="app.tsx")
app = FastAPI(docs_url="/api/docs", redoc_url="/api/redoc", lifespan=inertia_lifespan)

# Mount static files for examples
content_dir = Path(__file__).parent / "content"
app.mount(
    "/examples", StaticFiles(directory=str(content_dir / "examples")), name="examples"
)

# Add docs routes - that's it!
docs = CrossDocs()
docs.mount(app)
