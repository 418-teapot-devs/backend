import os
import sys
import uvicorn
import pytest


test = "tests" in sys.argv
os.environ["PYROBOTS_ASSETS"] = "tests/assets" if test else "app/assets"

if __name__ == "__main__":
    if test:
        pytest.main(["-x", "tests"])
    else:
        uvicorn.run("app.main:app", reload=True)
