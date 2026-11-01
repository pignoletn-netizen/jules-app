@echo off
chcp 65001 >nul
title Studio Montage Vidéo et Voix Off IA
color 0b

echo ======================================================================
echo           STUDIO DE MONTAGE VIDEO AUTOMATISE ET VOIX OFF IA
echo ======================================================================
echo.
echo Verification de l'environnement Python...

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] Python n'est pas detecte dans votre variable PATH.
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    echo Pensez a bien cocher la case "Add Python to PATH" lors de l'installation.
    echo.
    pause
    exit /b 1
)

echo Python detecte avec succes.
echo Verification et installation rapide des modules necessaires...
echo.

python -m pip install -q -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [ATTENTION] L'installation via pip a rencontre une erreur ou des paquets manquent.
    echo Tentative de poursuite du lancement...
)

echo.
echo ======================================================================
echo Lancement du Studio de Montage dans votre navigateur web...
echo L'application va s'ouvrir automatiquement sur http://localhost:8501
echo Gardez cette fenetre ouverte pendant l'utilisation.
echo Pour quitter l'application, fermez simplement cette fenetre.
echo ======================================================================
echo.

python -m streamlit run app_montage.py --server.port=8501 --server.headless=false

pause
