from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import (
    auth_router, habits_router, cycles_router, chatbot_router,
    community_router, medications_router, mood_router, tips_router, schemes_router,
)

# Creates tables on startup if they don't exist yet.
# For production, switch to Alembic migrations instead of this.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwasthyaSarthi AI API", version="0.1.0")

# CORS — allow the Vite dev server (and your deployed frontend URL later) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        # add your deployed frontend URL here before the hackathon demo
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(habits_router.router)
app.include_router(cycles_router.router)
app.include_router(chatbot_router.router)
app.include_router(community_router.router)
app.include_router(medications_router.router)
app.include_router(mood_router.router)
app.include_router(tips_router.router)
app.include_router(schemes_router.router)


@app.get("/")
def root():
    return {"status": "SwasthyaSarthi AI backend is running", "docs": "/docs"}