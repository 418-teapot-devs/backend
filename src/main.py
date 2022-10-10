from fastapi import FastAPI

from views.users import router as UserRouter

app = FastAPI(
    title="PyRobots API",
)

app.include_router(UserRouter, prefix="/users")


@app.get("/")
async def root():
    return {"msg": "Welcome to PyRobots!"}
