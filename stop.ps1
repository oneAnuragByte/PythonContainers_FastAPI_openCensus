#stop all running containers (assuming, containers running are related to this projct only)
docker stop $(docker ps -q)

#remove all the build docker image
docker image rm (docker image ls -q)
