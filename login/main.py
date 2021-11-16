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
from opencensus.trace.span_context import SpanContext

app = FastAPI()

#get connection string from environment variable set
appinsights_connString = os.environ.get("APPINSIGHT_CONN_KEY", False)

HTTP_URL = COMMON_ATTRIBUTES['HTTP_URL']
HTTP_STATUS_CODE = COMMON_ATTRIBUTES['HTTP_STATUS_CODE']

#callback to set Cloud role name
def callback_add_role_name(envelope):
    envelope.tags["ai.cloud.role"] = "login-v4"
    return True

#---set logger to forward logs to ApplicationInsights
logger = logging.getLogger(__name__)
handler = AzureLogHandler(connection_string=appinsights_connString)
handler.add_telemetry_processor(callback_add_role_name)
logger.addHandler(handler)


# fastapi middleware for opencensus
@app.middleware("http")
async def middlewareOpencensus(request: Request, call_next):
    
    exporter=AzureExporter(connection_string=appinsights_connString)
    exporter.add_telemetry_processor(callback_add_role_name)

    #<updated>*****************
    trace_parent_header = request.headers['traceparent']
    traceparent_split = trace_parent_header.split(sep='-')
    trace_id = traceparent_split[1]
    parent_id = traceparent_split[2]
    #</updated>*****************
    
    span_context = SpanContext(trace_id=trace_id, span_id=parent_id)
    tracer = Tracer(exporter=exporter,sampler=ProbabilitySampler(1.0), span_context=span_context)

    with tracer.span(name="login") as span:
        span.span_kind = SpanKind.SERVER

        #<debug>*******************
        print(f"SPAN {span.span_id}" )
        print(f"Trace ID {span.context_tracer.trace_id}" )

        #</debug>*****************
        
        response = await call_next(request)

        tracer.add_attribute_to_current_span(
            attribute_key=HTTP_STATUS_CODE,
            attribute_value=response.status_code)
        tracer.add_attribute_to_current_span(
            attribute_key=HTTP_URL,
            attribute_value=str(request.url))

    return response

@app.get("/login")
async def root(request: Request):

    #-----Date time---#
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    #-----------------#

    return {"message": "you are logged in"}