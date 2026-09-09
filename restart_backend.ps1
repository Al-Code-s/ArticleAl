param(
    [string]$PythonExecutable = "",
    [switch]$Elevated
)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $projectRoot "backend"

function Get-Port3000ListenerPids {
    return @(netstat -ano |
        Select-String '(0\.0\.0\.0:3000|\[::\]:3000)\s+.*LISTENING' |
        ForEach-Object { [int](($_ -split '\s+')[-1]) } |
        Sort-Object -Unique)
}

Write-Host "Stopping processes listening on port 3000..." -ForegroundColor Yellow
$listenerPids = @(Get-Port3000ListenerPids)
if ($listenerPids.Count -gt 0) {
    Write-Host "Found PIDs: $($listenerPids -join ', ')" -ForegroundColor Cyan
}
foreach ($listenerPid in $listenerPids) {
    try {
        Stop-Process -Id $listenerPid -Force -ErrorAction Stop
        Write-Host "Stopped PID $listenerPid"
    } catch {
        Write-Warning "Could not stop PID ${listenerPid}: $($_.Exception.Message)"
    }
}
Start-Sleep -Seconds 1
$remainingPids = @(Get-Port3000ListenerPids)
if ($remainingPids.Count -gt 0) {
    Write-Host "Port 3000 is still occupied by PIDs: $($remainingPids -join ', ')" -ForegroundColor Red
    if (-not $Elevated) {
        Write-Host "Requesting administrator permission in a new PowerShell window..." -ForegroundColor Yellow
        $arguments = @('-NoExit', '-ExecutionPolicy', 'Bypass', '-File', ('"{0}"' -f $MyInvocation.MyCommand.Path), '-Elevated')
        if ($PythonExecutable) {
            $arguments += @('-PythonExecutable', ('"{0}"' -f $PythonExecutable))
        }
        Start-Process powershell.exe -Verb RunAs -ArgumentList $arguments
        return
    }
    throw "Unable to release port 3000 even with administrator permission. PIDs: $($remainingPids -join ', ')"
}

if (-not $PythonExecutable) {
    $backendVenvPython = Join-Path $backendDir ".venv\Scripts\python.exe"
    $rootVenvPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (Test-Path $backendVenvPython) {
        $PythonExecutable = $backendVenvPython
    } elseif (Test-Path (Join-Path $projectRoot ".uv-python\cpython-3.12.14-windows-x86_64-none\python.exe")) {
        $PythonExecutable = Join-Path $projectRoot ".uv-python\cpython-3.12.14-windows-x86_64-none\python.exe"
    } elseif (Test-Path $rootVenvPython) {
        $PythonExecutable = $rootVenvPython
    } else {
        $PythonExecutable = (Get-Command python -ErrorAction Stop).Source
    }
}

Set-Location $backendDir
Write-Host "Starting ArticleAI backend from $backendDir" -ForegroundColor Green
& $PythonExecutable -m uvicorn main:app --reload --host 0.0.0.0 --port 3000
