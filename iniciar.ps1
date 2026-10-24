$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
Start-Process -FilePath "$PSScriptRoot\.venv\Scripts\pythonw.exe" -ArgumentList "`"$PSScriptRoot\app_desktop.py`"" -WorkingDirectory $PSScriptRoot
