### SELF-ELEVATION ###

# Get the ID and security principal of the current user account
$myWindowsID = [System.Security.Principal.WindowsIdentity]::GetCurrent()
$myWindowsPrincipal = New-Object System.Security.Principal.WindowsPrincipal($myWindowsID)

# Check to see if we are currently running "as Administrator"
if (-not $myWindowsPrincipal.IsInRole([System.Security.Principal.WindowsBuiltInRole]::Administrator)) {
    # We are not running "as Administrator" - so relaunch as administrator
    $process = Start-Process -FilePath "PowerShell" -ArgumentList $myInvocation.MyCommand.Definition -Verb RunAs -Wait -PassThru
    exit $process.ExitCode
}

### CREATE SCHEDULED TASK ###

$taskName = 'OpenRGB_HueClient'
$scriptPath = Resolve-Path -Path (Join-Path -Path $PSScriptRoot -ChildPath '..\run_silent.vbs')
Write-Host "Script path: $scriptPath"
$scriptCwd = Split-Path -Path $scriptPath -Parent
Write-Host "Script CWD: $scriptCwd"
$action = New-ScheduledTaskAction -Execute 'wscript.exe' -Argument $scriptPath -WorkingDirectory $scriptCwd
$trigger = New-ScheduledTaskTrigger -AtStartup
$trigger.Delay = 'PT30S' # 30 seconds delay

# register new task
Write-Host "Registering new task..."
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Force

Start-Sleep -Seconds 1

# run the task immediately
Write-Host "Starting task..."
Start-ScheduledTask -TaskName $taskName
