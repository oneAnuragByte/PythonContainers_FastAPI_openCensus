import requests
import logging
import os
from fastapi import FastAPI,Request
from datetime import datetime
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer
from opencensus.trace.span import SpanKind
from opencensus.trace.attributes_helper import COMMON_ATTRIBUTES

app = FastAPI()

#get connection string from environment variable set
appinsights_connString = os.environ.get("APPINSIGHT_CONN_KEY", False)

HTTP_URL = COMMON_ATTRIBUTES['HTTP_URL']
HTTP_STATUS_CODE = COMMON_ATTRIBUTES['HTTP_STATUS_CODE']

#callback to set Cloud role name
def callback_add_role_name(envelope):
    envelope.tags["ai.cloud.role"] = "front-end-v4"
    return True

#---set logger to forward logs to ApplicationInsights
logger = logging.getLogger(__name__)
handler = AzureLogHandler(connection_string=appinsights_connString)
handler.add_telemetry_processor(callback_add_role_name)
logger.addHandler(handler)


#whether running in container, the env variable is being set in dockerfile
runningInContainer = os.environ.get("IN_CONTAINER", False)

# fastapi middleware for opencensus
@app.middleware("http")
async def middlewareOpencensus(request: Request, call_next):
    
    exporter=AzureExporter(connection_string=appinsights_connString)
    exporter.add_telemetry_processor(callback_add_role_name)

    tracer = Tracer(exporter=exporter,sampler=ProbabilitySampler(1.0))
    
    with tracer.span(name="front-end") as span:
        span.span_kind = SpanKind.SERVER
        
        #<debug>*******************
        print(f"SPAN {span.span_id}" )
        print(f"Trace ID {span.context_tracer.trace_id}" )
        
        request.state.span_id = str(span.span_id)
        request.state.traceid = str(span.context_tracer.trace_id)
        

        #</debug>*****************
        response = await call_next(request)

        tracer.add_attribute_to_current_span(
            attribute_key=HTTP_STATUS_CODE,
            attribute_value=response.status_code)
        tracer.add_attribute_to_current_span(
            attribute_key=HTTP_URL,
            attribute_value=str(request.url))

    return response

@app.get("/me")
async def root(request: Request):
    
    #-----Date time---#
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    #-----------------#
    
    response = ''

    if runningInContainer:
        #response = requests.get(url='http://host.docker.internal:8002/login')
        header={"traceparent":f"00-{request.state.traceid}-{request.state.span_id}-01"}
        
        response = requests.get(url='http://host.docker.internal:8002/login', 
                headers=header)
        
        #response = requests.get(url="https://reqres.in/api/products/1")
    else:
        response = requests.get(url='http://localhost:8002/login')    
        #response = requests.get(url="https://reqres.in/api/products/1")      

    return response.json()