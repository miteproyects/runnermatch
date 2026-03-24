"""
RunnerMatch - API Endpoints
FastAPI routes for the application.
"""

from fastapi import FastAPI
from fastapi.cors import CORSMiddleware
import auth
import database
import matches
import verification
import profile

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_stard=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================
