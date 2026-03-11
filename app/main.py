from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import user_router, department_router

app = FastAPI(title="Propig Challenge API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router.router)
app.include_router(department_router.router)

@app.get("/")
async def root():
    return {"message": "API is running!"}