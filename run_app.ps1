# Amazon AutoList Studio PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "      Starting Amazon AutoList Studio...               " -ForegroundColor Yellow
Write-Host "      Store Profile: Manasvini Fancy                   " -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

$venvPython = "C:\Users\Haris\venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    & $venvPython -m streamlit run app.py
} else {
    python -m streamlit run app.py
}
