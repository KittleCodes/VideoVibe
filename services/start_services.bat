@echo off
setlocal

rem List of service directories
set services=api-gateway authentication channel engagement frontend notification recommendation user video

for %%s in (%services%) do (
    start powershell -NoExit -Command "cd .\%%s\src; python main.py"
)

endlocal
