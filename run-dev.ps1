[CmdletBinding()]
param(
    [string]$BindAddress = "127.0.0.1",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python executable not found on PATH. Install Python and ensure it is available before running this script."
}

function Import-DotEnv {
    param(
        [string]$Path = ".env"
    )

    if (-not (Test-Path $Path)) {
        return
    }

    Get-Content $Path | ForEach-Object {
        $line = $_.Trim()
        if (-not $line -or $line.StartsWith('#')) {
            return
        }

        $parts = $line -split '=', 2
        if ($parts.Count -ne 2) {
            return
        }

        $name = $parts[0].Trim()
        $value = $parts[1].Trim().Trim('"')

        if ($name) {
            Set-Item -Path Env:$name -Value $value
        }
    }
}

Import-DotEnv

if (-not $PSBoundParameters.ContainsKey('BindAddress') -and $env:APP_HOST) {
    $BindAddress = $env:APP_HOST
}

if (-not $PSBoundParameters.ContainsKey('Port') -and $env:APP_PORT) {
    [int]$Port = $env:APP_PORT
}

Write-Host ("Starting FastAPI development server on http://{0}:{1} (Ctrl+C to stop)." -f $BindAddress, $Port) -ForegroundColor Green

python -m uvicorn app.main:app --reload --host $BindAddress --port $Port
