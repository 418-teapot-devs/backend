from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/")
async def root_teapot():
    raise HTTPException(status_code=418, detail="I'm a failing teapot")


@router.get("/{name}")
async def read_teapot(name: str):
    return {"msg": f"Hola teapot {name}"}
