# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, questions, user_progress, stats


app = FastAPI()

origins = [
    "https://tgapp-frontend.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(questions.router)
app.include_router(user_progress.router)
app.include_router(stats.router)