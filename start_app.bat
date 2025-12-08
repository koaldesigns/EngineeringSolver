@echo off
echo Starting Engineering Equation Solver...

:: Start Backend
echo Starting Backend Server...
cd backend
start "EES Backend" cmd /k "uvicorn main:app --reload --port 8000"
cd ..

:: Start Frontend
echo Starting Frontend Server...
cd frontend
start "EES Frontend" cmd /k "npm run dev"
cd ..

:: Wait for servers to initialize
echo Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

:: Open Browser
echo Opening Web UI...
start chrome http://localhost:5173

echo Done!
