$version = $args[0]
$ApplicationInsights_ConnectionString = $args[1]

if($null -eq $version -or $version -eq "")
{
    Write-Output "No version specified. Specify version as first parameter.`nExiting..."
    exit
}

$login_image = "login:$version"

#Build docker image

docker build -t $login_image .

#show details of images build
docker image ls

#run after setting version
$env:APPINSIGHT_CONN_KEY = $ApplicationInsights_ConnectionString

docker run --rm -p 8002:8000 -e APPINSIGHT_CONN_KEY=$env:APPINSIGHT_CONN_KEY --name login $login_image
