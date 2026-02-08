# PowerShell script to build and push Docker images to GHCR
# Run this from the root of the project

$REGISTRY = "ghcr.io"
$OWNER = "${Env:GITHUB_REPOSITORY_OWNER}".ToLower() # Replace with your GitHub username if not set in environment

if (-not $OWNER) {
    Write-Host "Error: GITHUB_REPOSITORY_OWNER environment variable not set." -ForegroundColor Red
    Write-Host "Please set it or update this script with your GitHub username."
    $OWNER = Read-Host "Enter your GitHub username"
    $OWNER = $OWNER.ToLower()
}

$BACKEND_IMAGE = "${REGISTRY}/${OWNER}/family-backend:latest"
$FRONTEND_IMAGE = "${REGISTRY}/${OWNER}/family-frontend:latest"

Write-Host "Logging in to GHCR..." -ForegroundColor Cyan
# This assumes you have a Personal Access Token (PAT) with 'write:packages' scope
echo "Please ensure you have a GitHub Personal Access Token (PAT) ready."
$TOKEN = Read-Host "Enter your GitHub PAT" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($TOKEN)
$PLAIN_TOKEN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

echo $PLAIN_TOKEN | docker login $REGISTRY -u $OWNER --password-stdin

Write-Host "Building Backend image..." -ForegroundColor Cyan
docker build -t $BACKEND_IMAGE ./Backend

Write-Host "Pushing Backend image..." -ForegroundColor Cyan
docker push $BACKEND_IMAGE

Write-Host "Building Frontend image..." -ForegroundColor Cyan
docker build -t $FRONTEND_IMAGE ./Frontend

Write-Host "Pushing Frontend image..." -ForegroundColor Cyan
docker push $FRONTEND_IMAGE

Write-Host "Done!" -ForegroundColor Green
