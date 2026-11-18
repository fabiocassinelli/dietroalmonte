@echo off
rem Dietro al Monte - doppio clic per eseguire. Non serve digitare nulla.
title Dietro al Monte - Nuova ricerca
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel%==0 (
  python "scripts\nuova_ricerca.py" --pausa %*
) else (
  where py >nul 2>nul
  if errorlevel 1 (
    echo Non trovo Python. Installalo da https://www.python.org/downloads/windows/
    echo spuntando "Add python.exe to PATH", poi riprova.
    pause
    exit /b 1
  )
  py -3 "scripts\nuova_ricerca.py" --pausa %*
)
