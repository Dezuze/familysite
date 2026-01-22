$ErrorActionPreference = "Stop"

# 1. Init Swarm if not active
$swarmStatus = docker info --format '{{.Swarm.LocalNodeState}}'
if ($swarmStatus -ne "active") {
    Write-Host "Initializing Docker Swarm..." -ForegroundColor Cyan
    docker swarm init
}

# 2. Ensure Registry is running (outside of stack for persistence/build availability)
if (!(docker ps -q -f name=local_registry)) {
    Write-Host "Starting Local Registry..." -ForegroundColor Cyan
    docker run -d -p 5000:5000 --restart=always --name local_registry registry:2
}

# 3. Build & Push Images
Write-Host "Building and Pushing Images..." -ForegroundColor Cyan

# Backend
docker build -t 127.0.0.1:5000/family-backend:latest ./Backend
docker push 127.0.0.1:5000/family-backend:latest

# Frontend
docker build -t 127.0.0.1:5000/family-frontend:latest ./Frontend
docker push 127.0.0.1:5000/family-frontend:latest

# 4. Deploy Stack
Write-Host "Deploying Stack to Swarm..." -ForegroundColor Green
docker stack deploy -c docker-compose.yml family_app

Write-Host "Deployment Complete! Check status with: docker service ls" -ForegroundColor Green
