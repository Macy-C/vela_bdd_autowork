@echo on

net start "PmsCT Logger Service"
net start "PmsCT Messaging Service"
net start "PmsCT Printing Service"
net start "PmsCT Remoting Service"

start "" "C:\usr\diamond.root\bin\gantryservers\CanBusSimulator.exe"
start "" "C:\usr\diamond.root\bin\gantryservers\CANMSEngine.exe" 
start "" "C:\usr\diamond.root\bin\gantryservers\GantryWCFSelfHostedServices.exe"

call :wait_seconds 5

#start "" "C:\Pms\System\Workflow.exe"

start c:\pms\system\PmsWindowsPrinting.exe
:PrintingServiceRunning
cd c:\pms\bin
c:\pms\bin\Product.Logon.Philips_Service.cmd

exit /b %ERRORLEVEL%

:wait_seconds
set /a WAIT_PINGS=%~1 + 1
ping -n %WAIT_PINGS% 127.0.0.1 >nul
exit /b 0