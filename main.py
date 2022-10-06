from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/")
async def read_root():
    return {"msg": "Hola tetera"}

@app.get("/tetera")
async def read_tetera():
    raise HTTPException(status_code=418, detail="I'm a teapot")

@app.get("/{id}")
async def read_root(id):
    return { "msg": f"Hola {id}" }
