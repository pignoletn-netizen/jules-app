@echo off
chcp 65001 >nul
title Installation des dependances - Studio Montage Video
color 0a

echo ======================================================================
echo    INSTALLATION DES MODULES DU STUDIO DE MONTAGE VIDEO
echo ======================================================================
echo.

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Python n'a pas ete trouve.
    echo Installez Python 3.10 ou superieur en cochant "Add Python to PATH".
    pause
    exit /b 1
)

echo Mise a niveau de pip...
python -m pip install --upgrade pip

echo.
echo Installation de toutes les bibliotheques requises (requirements.txt)...
python -m pip install -r requirements.txt

echo.
echo ======================================================================
echo [SUCCES] L'installation est terminee !
echo Vous pouvez maintenant double-cliquer sur "lancer_application.bat"
echo pour demarrer l'application a tout moment.
echo ======================================================================
echo.
pause
