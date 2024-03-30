from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# "Mounting" means adding a complete "independent" application in a specific path, that then takes care of handling all the sub-paths.
# way to combine multiple FastAPI applications into a single server.
app.mount("/static", StaticFiles(directory="static"), name="static")