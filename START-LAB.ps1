$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
New-Item -ItemType Directory -Force -Path '.local' | Out-Null
Start-Process -FilePath 'python' -ArgumentList '-m http.server 8010 --bind 127.0.0.1 --directory public' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput '.local/server.log' -RedirectStandardError '.local/server-error.log'
Start-Process -FilePath 'node' -ArgumentList 'scripts/publish.mjs --watch' -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput '.local/publish.log' -RedirectStandardError '.local/publish-error.log'
Start-Process 'http://127.0.0.1:8010'
