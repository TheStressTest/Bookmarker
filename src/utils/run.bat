:: small script which lets me run the bot in all environments

@echo off

:: allowd parent dir imports
set PYTHONPATH=%cd%

echo "%PYTHONPATH%"

%cd%\Venv\Scripts\python.exe src\bot.py