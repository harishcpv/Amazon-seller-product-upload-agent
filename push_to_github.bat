@echo off
echo ========================================================
echo       Pushing Amazon AutoList Studio to GitHub
echo       Target: https://github.com/harishcpv/amazon-autolist-studio.git
echo ========================================================
echo.
echo Make sure you have created the empty repository on GitHub:
echo https://github.com/new (Repository name: amazon-autolist-studio)
echo.
git remote set-url origin https://github.com/harishcpv/amazon-autolist-studio.git
git push -u origin main
echo.
pause
