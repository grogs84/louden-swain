#!/usr/bin/env python3
"""
Simple FastAPI app for debugging Railway deployment issues
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="NCAA Wrestling Championship API - Debug Version")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "NCAA Wrestling Championship API - Debug Version",
        "status": "healthy",
        "port": os.getenv("PORT", "8000"),
        "env_vars": {
            "USE_DUCKDB": os.getenv("USE_DUCKDB"),
            "DATABASE_URL_SET": bool(os.getenv("DATABASE_URL")),
            "SUPABASE_URL_SET": bool(os.getenv("SUPABASE_URL")),
            "SUPABASE_KEY_SET": bool(os.getenv("SUPABASE_KEY"))
        }
    }

@app.get("/debug")
async def debug():
    """Debug endpoint to check environment"""
    return {
        "environment_variables": {
            key: "***" if "KEY" in key or "PASSWORD" in key or "SECRET" in key else value
            for key, value in os.environ.items()
            if key.startswith(("DATABASE", "SUPABASE", "USE_", "PORT"))
        }
    }

@app.get("/health")
async def health():
    """Simple health check"""
    return {"status": "ok", "message": "App is running"}
