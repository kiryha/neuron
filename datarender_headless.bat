@echo off
setlocal
title Neuron Headless Dataset Render

rem Render settings. For a DEV pilot, change MATERIAL_JSON and DATASET_NAME.
set "HYTHON=E:\Programs\Houdini22.0.368\bin\hython.exe"
set "SCENE=C:\Users\kko8\OneDrive\projects\neuron\prod\3D\scenes\material_hero_006.hiplc"
set "MATERIAL_JSON=C:\Users\kko8\OneDrive\dev\neuron\datagen\data\neuron_library_prod.json"
set "DATASET_ROOT=E:\Projects\neuron_data\datasets"
set "DATASET_NAME=material_hero_v0"
set "GEOMETRY=sculpted_rubber_toy"
set "CAMERA=cam_001"

if not exist "%HYTHON%" (
    echo ERROR: hython.exe not found: %HYTHON%
    goto :failed
)

if not exist "%SCENE%" (
    echo ERROR: Houdini scene not found: %SCENE%
    goto :failed
)

if not exist "%MATERIAL_JSON%" (
    echo ERROR: Material JSON not found: %MATERIAL_JSON%
    goto :failed
)

"%HYTHON%" "%~dp0datagen\datarender_headless.py" ^
    --scene "%SCENE%" ^
    --material-json "%MATERIAL_JSON%" ^
    --dataset-root "%DATASET_ROOT%" ^
    --dataset-name "%DATASET_NAME%" ^
    --geometry "%GEOMETRY%" ^
    --camera "%CAMERA%"

set "EXIT_CODE=%ERRORLEVEL%"
echo.
if "%EXIT_CODE%"=="0" (
    echo Headless dataset render finished successfully.
) else (
    echo Headless dataset render stopped with exit code %EXIT_CODE%.
)
pause
exit /b %EXIT_CODE%

:failed
echo.
pause
exit /b 1
