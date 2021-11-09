from fastapi import FastAPI,Request
import requests
app = FastAPI()

@app.get("/me")
async def root(request: Request):
    #logger.warning('Holaaa alguine me esta haciendo un request', extra=properties)
    
    # parent_from_req = request.state.parentid
    # trace_rq = request.state.traceid
    # print(f"SPAN from req {parent_from_req}" )
    #response = requests.get(url='http://localhost:8081/login',headers={"parent-span-id":parent_from_req,"parent-trace-id":trace_rq})
    
    #return response.json()
    return {"message": "Hello World! from Container"}