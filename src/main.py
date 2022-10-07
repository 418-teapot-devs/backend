from fastapi import FastAPI

from views.teapot import router as TeapotRouter

app = FastAPI(
    title="PyRobots API",
)


@app.get("/")
async def read_root():
    return {"msg": "Hola tetera"}


@app.get("/{id}")
async def read_root(id):
    return {"msg": f"Hola {id}"}


app.include_router(TeapotRouter, prefix="/teapot")
