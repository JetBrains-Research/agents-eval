# Project Template Generation Environment Based on Code Engine

## Setup Docker Image
1. Download code-engine distributive to the current directory (`[code-ai-agents-service-app-0.3.95](code-ai-agents-service-app-0.3.95))
2. Check the app version equals to ones mentioned in [Dockerfile](Dockerfile)
3. Run docker build
```commandline 
docker build -t username/code-engine .
```
4. Push docker image to docker hub
```commandline
docker push username/code-engine
```
5. Run docker image
```commandline
docker run -it -p 5050:5050 username/code-engine
```