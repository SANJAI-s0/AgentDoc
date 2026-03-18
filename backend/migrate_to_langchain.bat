@echo off
REM Migration script from CrewAI to LangChain (Windows)

echo =========================================
echo AgentDoc: CrewAI to LangChain Migration
echo =========================================
echo.

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Warning: No virtual environment detected
    echo Please activate your virtual environment first:
    echo   .venv\Scripts\activate
    exit /b 1
)

echo Virtual environment detected: %VIRTUAL_ENV%
echo.

REM Uninstall CrewAI
echo Step 1: Uninstalling CrewAI...
pip uninstall crewai crewai-tools -y
if %ERRORLEVEL% EQU 0 (
    echo CrewAI uninstalled successfully
) else (
    echo Warning: CrewAI uninstall had issues ^(may not be installed^)
)
echo.

REM Install LangChain
echo Step 2: Installing LangChain...
pip install langchain langchain-google-genai
if %ERRORLEVEL% EQU 0 (
    echo LangChain installed successfully
) else (
    echo Error: LangChain installation failed
    exit /b 1
)
echo.

REM Install all requirements
echo Step 3: Installing all requirements...
pip install -r requirements.txt
if %ERRORLEVEL% EQU 0 (
    echo All requirements installed
) else (
    echo Warning: Some requirements may have failed
)
echo.

REM Verify installation
echo Step 4: Verifying installation...
python -c "import langchain; print('LangChain version:', langchain.__version__)"
python -c "import langchain_google_genai; print('LangChain Google GenAI installed')"
echo.

REM Check for CrewAI (should not be present)
python -c "import crewai" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo CrewAI successfully removed
) else (
    echo Warning: CrewAI still detected
)
echo.

echo =========================================
echo Migration Complete!
echo =========================================
echo.
echo Next steps:
echo 1. Test the application: python manage.py runserver
echo 2. Upload a test document to verify functionality
echo 3. Check logs for any errors
echo.
echo For more information, see MIGRATION_TO_LANGCHAIN.md
pause
