### CHECK CWD ###

if (-not (Test-Path -Path 'hueclient\__init__.py')) {
    Write-Host "Please run this script from the root directory of the project (e.g. .\scripts\install.ps1)."
    exit 1
}

### REMOVE SCHEDULED TASK ###

.\scripts\unregister_task.ps1
