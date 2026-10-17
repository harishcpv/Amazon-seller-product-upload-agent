@echo off
title Amazon AutoList Studio - Manasvini Fancy
echo ========================================================
echo       Starting Amazon AutoList Studio...
echo       Store Profile: Manasvini Fancy
echo ========================================================
echo.

IF EXIST "C:\Users\Haris\venv\Scripts\activate.bat" (
    call "C:\Users\Haris\venv\Scripts\activate.bat"
    streamlit run app.py
) ELSE (
    python -m streamlit run app.py
)

pause
