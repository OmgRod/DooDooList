@echo off
if exist ".venv" (
    call ".venv\Scripts\activate"
) else (
    py -3.10 -m venv ".venv"
    call ".venv\Scripts\activate"
)