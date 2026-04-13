# Start the Medical Assistant FastAPI backend (listens on http://127.0.0.1:8000)
Set-Location $PSScriptRoot\server
& "$PSScriptRoot\.venv\Scripts\uvicorn.exe" main:app --reload --host 127.0.0.1 --port 8000
