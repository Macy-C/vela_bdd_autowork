@echo on

net start "PmsCT Logger Service"
net start "PmsCT Messaging Service"
net start "PmsCT Printing Service"
net start "PmsCT Remoting Service"
net start "Gantry Services"
net start "GantryLoggerHost"

start "" "C:\usr\diamond.root\bin\gantryservers\CanBusSimulator.exe"
start "" "C:\usr\diamond.root\bin\gantryservers\CANMSEngine.exe" 
start "" "C:\usr\diamond.root\bin\gantryservers\GantryWCFSelfHostedServices.exe"




call :wait_seconds 5


echo Starting System Simulator Engine...
start "" "C:\Pms\Simulators\SystemSimulator\Server\SimulatorEngine.exe"

call :wait_seconds 5

echo Starting System Simulator Client...
start "" "C:\Pms\Simulators\SystemSimulator\Client\Simulators.exe"

call :wait_seconds 15
exit /b %ERRORLEVEL%

:wait_seconds
set /a WAIT_PINGS=%~1 + 1
ping -n %WAIT_PINGS% 127.0.0.1 >nul
exit /b 0