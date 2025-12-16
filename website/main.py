from cross_docs import CrossDocs
from fastapi import FastAPI
from inertia import configure_inertia
from inertia.fastapi.experimental import inertia_lifespan

configure_inertia(vite_entry="app.tsx")
app = FastAPI(docs_url="/api/docs", redoc_url="/api/redoc", lifespan=inertia_lifespan)
# Add docs routes - that's it!
docs = CrossDocs()
docs.mount(app)
