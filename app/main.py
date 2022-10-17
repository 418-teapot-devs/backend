from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from views.users import router as UserRouter
from views.robots import router as RobotRouter
from views.created import router as CreatedRouter
from views.joined import router as JoinedRouter
from views.public import router as PublicRouter

app = FastAPI(
    title="PyRobots API",
)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(UserRouter, prefix="/users")
app.include_router(RobotRouter, prefix="/robots")
app.include_router(CreatedRouter, prefix="/matches")
app.include_router(JoinedRouter, prefix="/matches")
app.include_router(PublicRouter, prefix="/matches")


@app.get("/")
def root():
    return {"msg": "Welcome to PyRobots!"}
