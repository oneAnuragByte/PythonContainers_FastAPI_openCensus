# Sample Python FASTAPI application with 2 docker container and connected to Azure Application Insights. 

This is to implement telemetry correlation and trace request as it leaves one container and reaches the other through [Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview). 

### Resources
1. [Telemetry correlation in Application Insights](https://docs.microsoft.com/en-us/azure/azure-monitor/app/correlation#example)
2. [Telemetry correlation in OpenCensus Python](https://docs.microsoft.com/en-us/azure/azure-monitor/app/correlation#telemetry-correlation-in-opencensus-python)

### Using this sample
Pre-requisite

* Docker desktop installed and running (I used Docker desktop on Windows. This should work on Linux as well, except the internal routing between one container to other which *might* need modification in `root()` method of `frontend\main.py`).

Running the containers
1. Navigate to frontend\ directory and run `start.ps1` in powershell, using the following parameters. 
    `start.ps1 <version> <InstrumentationKey in "InstrumentationKey=<> format">`

    **Example**: `start.ps1 1.0.0 InstrumentationKey=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX`

2. Navigate to login\ directory and run `start.ps1` in powershell, using similar parameters as above. 
3. 2 Containers will be running (check using `docker ps` in a new terminal)
4. Make request from browser to http://127.0.0.1/me to initiate request. The request lands in Front-end container and then gets forwarded to login container. The response from login is then routed through front-end back to browser. 
