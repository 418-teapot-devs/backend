from pydantic import BaseModel,HttpUrl 

class Create(BaseModel):
    name: str
    code: HttpUrl
    avatar: HttpUrl
