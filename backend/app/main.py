from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.models.database import Base, engine
from app.api import (
    events, sessions, venues, teams, tasks,
    dependencies, resources, volunteers, risks,
    impact, simulation, briefings, notion, knowledge
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Team Operations & Event Command Center with Directed Graph Dependency Engine and Notion Synchronization"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for local dev & demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(events.router, prefix=settings.API_PREFIX)
app.include_router(sessions.router, prefix=settings.API_PREFIX)
app.include_router(venues.router, prefix=settings.API_PREFIX)
app.include_router(teams.router, prefix=settings.API_PREFIX)
app.include_router(tasks.router, prefix=settings.API_PREFIX)
app.include_router(dependencies.router, prefix=settings.API_PREFIX)
app.include_router(resources.router, prefix=settings.API_PREFIX)
app.include_router(volunteers.router, prefix=settings.API_PREFIX)
app.include_router(risks.router, prefix=settings.API_PREFIX)
app.include_router(impact.router, prefix=settings.API_PREFIX)
app.include_router(simulation.router, prefix=settings.API_PREFIX)
app.include_router(briefings.router, prefix=settings.API_PREFIX)
app.include_router(notion.router, prefix=settings.API_PREFIX)
app.include_router(knowledge.router, prefix=settings.API_PREFIX)

@app.get("/")
def root():
    return {
        "system": "EVENTRA",
        "tagline": "The intelligence behind every moving part.",
        "status": "OPERATIONAL",
        "version": settings.VERSION,
        "docs_url": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "HEALTHY", "database": "CONNECTED"}
