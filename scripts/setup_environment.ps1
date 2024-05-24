# setup_environment.ps1
# Get the full path to the script's directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$basePath = Split-Path -Parent $scriptPath

# Set the current directory to the script's base path
$originalLocation = Get-Location
Set-Location $basePath

# Ensure the script can execute external scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
# Check if Python is installed
$pythonInstalled = $null
try {
    $pythonInstalled = Get-Command "python" -ErrorAction Stop
} catch {
    Write-Host "Python is not installed on your system."
}

if ($null -eq $pythonInstalled) {
    # Check if winget is available to install Python
    $wingetInstalled = $null
    try {
        $wingetInstalled = Get-Command "winget" -ErrorAction Stop
    } catch {
        Write-Host "Windows Package Manager (winget) is not available. You can install it in the Microsoft Store or from https://www.microsoft.com/p/app-installer/9nblggh4nns1#activetab=pivot:overviewtab"
    }

    if ($null -ne $wingetInstalled) {
        Write-Host "Attempting to install Python using Windows Package Manager (winget)..."
        winget install --id=Python.Python.3 -e --source winget
        # Verify installation
        try {
            $pythonInstalled = Get-Command "python" -ErrorAction Stop
            Write-Host "Python has been successfully installed."
        } catch {
            Write-Host "Failed to install Python. Please install it manually."
        }
    } else {
        Write-Host "Please install Python manually by downloading it from 'https://www.python.org/downloads/' or enable Windows Package Manager (winget) on your system."
    }
} else {
    Write-Host "Python is already installed."
}

# Create a Python virtual environment
Write-Host "Creating Python virtual environment."
python -m venv .venv

# Activate the virtual environment
#Write-Host "Activating Python virtual environment."
#.venv\Scripts\Activate.ps1

# Determine the correct path for the pip executable based on the OS
$venvPip = $null
if ($env:OS -eq "Windows_NT") {
    $venvPip = Join-Path -Path $basePath -ChildPath ".venv\Scripts\pip"
} else {
    $venvPip = Join-Path -Path $basePath -ChildPath ".venv/bin/pip"
}

Write-Host "Installing Python dependencies using venv's pip."
& $venvPip install -r "$basePath/backend/requirements.txt"

# Install Python packages from requirements.txt
Write-Host "Installing Python dependencies."
pip install -r backend\requirements.txt
# Check if npm is available
$npmInstalled = $null
try {
    $npmInstalled = Get-Command "npm" -ErrorAction Stop
} catch {
    Write-Host "npm is not installed. Please install Node.js which includes npm."
}

if ($null -eq $npmInstalled) {
    Write-Host "npm is not available. Checking for nvm..."
    # Check if nvm is available
    $nvmInstalled = $null
    try {
        $nvmInstalled = Get-Command "nvm" -ErrorAction Stop
    } catch {
        Write-Host "nvm-windows is not installed. Please install it from https://github.com/coreybutler/nvm-windows/releases"
        # Optionally, automate the download and installation here
    }

    if ($null -ne $nvmInstalled) {
        # Install the latest Node.js version
        nvm install latest
        nvm use latest
        Write-Host "Node.js has been successfully installed and set to the latest version."
    } else {
        Write-Host "Please follow the manual installation steps at https://learn.microsoft.com/en-us/windows/dev-environment/javascript/nodejs-on-windows"
    }
} else {
    # Change directory to frontend, install npm packages, and build the project
    Write-Host "Building frontend with Node.js."
    Push-Location frontend
    npm install
    npm run build
    Pop-Location
}

# Deactivate the Python virtual environment
#Write-Host "Deactivating virtual environment."
#cmd /c ".venv\Scripts\deactivate.bat"

Set-Location $originalLocation
