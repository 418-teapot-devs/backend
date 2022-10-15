from fastapi import Header, APIRouter, HTTPException, UploadFile
from jose import jwt
from pony.orm import commit, db_session, select
from core.models.user import User
from core.models.robot import Robot
from core.schemas.robot import Create
from views import get_current_user
import os

router = APIRouter()

@router.get("/")
def register(token:str = Header()):
    username = get_current_user(token)

    with db_session:
        res = []
        for r in select(r for r in Robot): #recordar lo de chequear
            print(r.id)
            if r.has_avatar:
                res.append({"name": r.name, "id": r.id, "avatar": f"assets/robots/{r.id}.png"})
            else:
                res.append({"name": r.name, "id": r.id, "avatar": None}) 

    return res

@router.post("/")
def upload_match(name: str, avatar: UploadFile | None = None, code: UploadFile | None = None, token: str = Header()):
    username =  get_current_user(token)

    with db_session:
        username = get_current_user(token)

        user = User.get(name=username)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")


        r = Robot(owner=user, name=name, has_avatar = avatar is not None)

        commit()
        path = "app/assets/robots"
        if not os.path.exists("app/assets/robots"):
            os.makedirs("app/assets/robots")
            print("directory created")

        if avatar:
            with open(f"app/assets/robots/{r.id}.png", "wb") as f:
                f.write(avatar.file.read())

        if code:
            with open(f"app/assets/robots/{r.id}.py", "wb") as f:
                f.write(code.file.read())

 
    return {}
