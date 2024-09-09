$FreedomOSDir = Split-Path -Path $PSScriptRoot -Parent
cd "$FreedomOSDir\ouroboros"
.\.venv\Scripts\Activate.ps1
wt --window 0 split-pane --title "Ouroboros" --startingDirectory "$FreedomOSDir\ouroboros" --profile "Windows PowerShell" PowerShell -noexit -command {.\.venv\Scripts\Activate.ps1; faststream run server:app --reload}
Start-Sleep -milliseconds 500
wt --window 0 new-tab --title "Frontend" --startingDirectory "$FreedomOSDir\client" --profile "Windows PowerShell" PowerShell -noexit -command {bun run dev}
