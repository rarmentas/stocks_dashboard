@echo off
cd /d "D:\Apps\01-Tickers\Real_Time_Stock_Price_Dashboard"

REM Check if conda is available
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Conda is not installed or not in PATH
    pause
    exit /b 1
)

REM Activate conda environment
call conda activate stockdashboard
if %errorlevel% neq 0 (
    echo Error: Failed to activate conda environment 'stockdashboard'
    echo Please make sure the environment exists
    pause
    exit /b 1
)

REM Check if app.py exists
if not exist "app.py" (
    echo Error: app.py not found in current directory
    pause
    exit /b 1
)

REM Run the Streamlit app
python -m streamlit run app.py

pause