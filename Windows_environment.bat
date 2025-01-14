@echo off
:: Create Virtual Environment
echo Creating virtual environment 'myenv'...
python -m venv myenv

:: Activate the Virtual Environment
echo Activating virtual environment...
call myenv\Scripts\activate

:: Install Packages
echo Installing Python packages from requirements.txt...
pip install -r requirements.txt

echo All packages installed successfully!
pause
