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

### KILL RUNNING SCRIPTS ###

# check for any instances of .venv\Scripts\python.exe
$runningScripts = Get-Process | Where-Object { $_.Path -like "*\.venv\Scripts\python.exe" }
if ($runningScripts) {
    Write-Host "Killing running scripts..."
    $runningScripts | ForEach-Object { Stop-Process -Id $_.Id -Force }
}

### REMOVE SCHEDULED TASK ###

$taskName = 'OpenRGB_HueClient'

# delete existing task
$taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
if ($taskExists) {
    Write-Host "Deleting existing task..."
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}
