### CHECK CWD ###

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -Path 'hueclient\__init__.py')) {
    Write-Host "Please run this script from the root directory of the project (e.g. .\scripts\install.ps1)."
    exit 1
}

### SETUP PYTHON ENVIRONMENT ###

if (-not (Test-Path -Path '.venv')) {
    # setup python virtual environment
    python3 -m venv .venv
    ./.venv/Scripts/Activate.ps1

    # install dependencies
    python -m pip install --upgrade pip
    pip install -r requirements.txt
}

### SETUP .env FILE ###

$envPath = '.env'

if (-not (Test-Path -Path '.env')) {
    # ask for hue bridge ip
    $bridgeIp = Read-Host -Prompt 'Enter the IP address of your Hue Bridge'

    # register the bridge
    Write-Host "Please press the Link button on your Hue Bridge now..."
    $bridgeUsername = python -m hueclient.tools.register_bridge "$bridgeIp" "openrgb-hueclient" "00:00:00:00:00:00"
    if (-not $bridgeUsername) {
        Write-Host "Failed to register with the Hue Bridge."
        exit 1
    }
    Write-Host "Successfully registered with the Hue Bridge."

    $bridgeRoom = Read-Host -Prompt 'Enter the name of the room you want to observe'

    $openrgbHost = Read-Host -Prompt 'Enter the IP address of your OpenRGB server (default: "localhost")'
    if (-not $openrgbHost) {
        $openrgbHost = 'localhost'
    }

    $openrgbPort = Read-Host -Prompt 'Enter the port of your OpenRGB server (default: "6742")'
    if (-not $openrgbPort) {
        $openrgbPort = '6742'
    }

    # write to .env file
    @"
BRIDGE_IP=$bridgeIp
BRIDGE_USERNAME=$bridgeUsername
BRIDGE_ROOM=$bridgeRoom

OPENRGB_HOST=$openrgbHost
OPENRGB_PORT=$openrgbPort
"@ | Set-Content -Path $envPath
}

### CREATE SCHEDULED TASK ###

.\scripts\unregister_task.ps1
.\scripts\register_task.ps1
