@echo off
echo =======================================================
echo Starting GuardMind Project Setup...
echo =======================================================
echo.

IF NOT EXIST ".venv" (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
) ELSE (
    echo [1/3] Virtual environment found.
)

echo [2/3] Installing dependencies (this may take a moment)...
call .\.venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

echo [3/3] Launching servers...
:: Open the API server in a new window
start "Guardrail API Server" cmd /c ".\.venv\Scripts\activate.bat && uvicorn api_server:app --reload --host 0.0.0.0 --port 8000"

:: Open the Chat Server in a new window
start "GuardMind Chat Server" cmd /c ".\.venv\Scripts\activate.bat && python chat_server.py"

echo.
echo =======================================================
echo ALL DONE!
echo - GuardMind Chat: http://localhost:5050
echo - Guardrail API : http://localhost:8000
echo.
echo Two new terminal windows have been opened for the servers.
echo You can close this window now.
echo =======================================================
pause
