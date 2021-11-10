from fastapi import FastAPI,Request
import requests
import logging

import os

app = FastAPI()
logger = logging.getLogger(__name__)

@app.get("/me")
async def root(request: Request):

    runningInContainer = os.environ.get("IN_CONTAINER", False)

    response = ''

    if runningInContainer:
        logger.info("Inside container")
        response = requests.get(url='http://host.docker.internal:8002/login')
    else:
        logger.info("not inside container")
        response = requests.get(url='http://localhost:8002/login')          

    return response.json()