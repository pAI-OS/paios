# remove_environment.ps1

# Get the full path to the script's directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$basePath = Split-Path -Parent $scriptPath

# Define paths to the directories to be removed
$venvPath = Join-Path -Path $basePath -ChildPath ".venv"
$nodeModulesPath = Join-Path -Path $basePath -ChildPath "frontend\node_modules"

# Function to remove a directory if it exists
function Remove-DirectoryIfExists {
    param (
        [string]$path
    )
    if (Test-Path $path) {
        Remove-Item -Path $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Removed directory: $path"
    }
    else {
        Write-Host "Directory not found: $path"
    }
}

# Remove the .venv directory
Write-Host "Removing Python virtual environment (backend)."
Remove-DirectoryIfExists -path $venvPath

# Remove the frontend/node_modules directory
Write-Host "Removing Node.js modules (frontend)."
Remove-DirectoryIfExists -path $nodeModulesPath
