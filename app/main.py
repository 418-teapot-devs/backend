from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.views.matches import router as MatchesRouter
from app.views.robots import router as RobotRouter
from app.views.simulate import router as SimulateRouter
from app.views.users import router as UserRouter

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
app.include_router(MatchesRouter, prefix="/matches")
app.include_router(SimulateRouter, prefix="/simulate")

app.mount(
    "/assets/avatars/users",
    StaticFiles(directory="app/assets/users"),
    name="useravatars",
)
app.mount(
    "/assets/avatars/robots",
    StaticFiles(directory="app/assets/robots"),
    name="robotavatars",
)


@app.get("/")
def root():
    return {"msg": "Welcome to PyRobots!"}
