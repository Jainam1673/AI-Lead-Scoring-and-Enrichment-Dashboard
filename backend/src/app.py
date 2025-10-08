from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.api import router

app = FastAPI(title="AI Lead Scoring API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "AI Lead Scoring API"}