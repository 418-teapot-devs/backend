import os
import sys

import coverage
import pytest
import uvicorn

testpaths = []
for arg in sys.argv:
    if arg.startswith("tests"):
        testpaths.append(arg)

test = len(testpaths) != 0

os.environ["PYROBOTS_DBFILE"] = ":sharedmemory:" if test else "db.sqlite"
os.environ["PYROBOTS_ASSETS"] = "tests/assets" if test else "app/assets"

if __name__ == "__main__":
    if test:
        cov = coverage.Coverage(omit=["tests/*"])
        cov.start()
        pytest.main(["-vvx", "--ignore-glob=tests/assets/*"] + testpaths)
        cov.stop()
        cov.save()
        cov.html_report()
    else:
        uvicorn.run("app.main:app", reload=True)
