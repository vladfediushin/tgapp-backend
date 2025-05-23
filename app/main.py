# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import questions, answers, stats


app = FastAPI()

origins = [
    "https://tgapp-frontend.vercel.app"
]

# разрешим CORS для локального фронта
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(questions.router)
app.include_router(answers.router)
app.include_router(stats.router)
