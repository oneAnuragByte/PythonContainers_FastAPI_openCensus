from fastapi import FastAPI,Request
import requests
app = FastAPI()

@app.get("/login")
async def root(request: Request):
   
    return {"message": "you are logged in"}