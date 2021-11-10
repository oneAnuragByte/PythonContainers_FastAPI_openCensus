from fastapi import FastAPI,Request
import requests
import logging
from datetime import datetime
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace import config_integration
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer

import os

app = FastAPI()

#get connection string from environment variable set
appinsights_connString = os.environ.get("APPINSIGHT_CONN_KEY", False)

#callback to set Cloud role name
def callback_add_role_name(envelope):
    envelope.tags["ai.cloud.role"] = "front-end"
    return True


#---set logger to forward logs to ApplicationInsights
logger = logging.getLogger(__name__)
handler = AzureLogHandler(connection_string=appinsights_connString)
handler.add_telemetry_processor(callback_add_role_name)
logger.addHandler(handler)


#---Dependency with "requests" integration, ref: https://docs.microsoft.com/en-us/azure/azure-monitor/app/opencensus-python-dependency#dependencies-with-requests-integration
config_integration.trace_integrations(['requests'])  # <-- this line enables the requests integration
exporter=AzureExporter(connection_string=appinsights_connString)
exporter.add_telemetry_processor(callback_add_role_name)
tracer = Tracer(exporter=exporter, sampler=ProbabilitySampler(1.0))


#whether running in container, the env variable is being set in dockerfile
runningInContainer = os.environ.get("IN_CONTAINER", False)

@app.get("/me")
async def root(request: Request):
    
    #-----Date time---#
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    #-----------------#

    logger.warning("Processing request at : " + current_time)
    
    response = ''

    with tracer.span(name="front-end"):
        if runningInContainer:
            #response = requests.get(url='http://host.docker.internal:8002/login')
            response = requests.get(url="https://reqres.in/api/products/1")
        else:
            #response = requests.get(url='http://localhost:8002/login')    
            response = requests.get(url="https://reqres.in/api/products/1")      

    return response.json()