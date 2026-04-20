@echo off
REM Windows quick setup script for Temporiq AI

echo "Temporiq AI - Quick Setup for Windows"
echo "========================================"

REM Check Python version
python --version

REM Create virtual environment
echo "Creating virtual environment..."
python -m venv .venv
call .venv\Scripts\activate.bat

REM Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

REM Create .env from template
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo WARNING: Please update the new .env file with your credentials.
)

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Update the .env file with your Supabase and Google Cloud credentials.
echo 2. In your terminal, set the GOOGLE_APPLICATION_CREDENTIALS variable.
echo    Example for Windows: set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\key.json"
echo 3. Run the app: streamlit run app.py
