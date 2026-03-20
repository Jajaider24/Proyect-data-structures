from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.export import router as trees_router
from api.routes.flights import router as flights_router
from api.routes.versions import router as versions_router


app = FastAPI(
	title="SkyBalance AVL API",
	description="API base para gestionar vuelos con arbol AVL y comparacion BST.",
	version="0.1.0",
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(flights_router)
app.include_router(versions_router)
app.include_router(trees_router)


@app.get("/")
def health() -> dict[str, str]:
	return {
		"service": "SkyBalance AVL",
		"status": "ok",
		"docs": "/docs",
	}