from fastapi import FastAPI
from app.routers import user_router, department_router

app = FastAPI(title="Propig Challenge API")

app.include_router(user_router.router)
app.include_router(department_router.router)

@app.get("/")
async def root():
    return {"message": "API is running!"}