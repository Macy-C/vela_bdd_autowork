@echo off
 
c:\Windows\System32\taskkill /im PmsRemotingService.exe /f /t
c:\Windows\System32\taskkill /im PmsPrintingService.exe /f /t
c:\Windows\System32\taskkill /im MessageService.exe /f /t
c:\Windows\System32\taskkill /im LoggerSvc.exe /f /t
c:\Windows\System32\taskkill /im WatchDogService.exe /f /t
c:\Windows\System32\taskkill /im PmsWindowsPrinting.exe /f /t
c:\Windows\System32\taskkill /im CardiacServer.exe /f /t
c:\Windows\System32\taskkill /im PmsWindowsPrinting.exe /f /t
c:\Windows\System32\taskkill /im IrsSim.exe /f /t
c:\Windows\System32\taskkill /im IrsSimUI.exe /f /t
c:\Windows\System32\taskkill /im LOGGER~1.exe /f /t
c:\Windows\System32\taskkill /im CANMSE~1.exe /f /t
c:\Windows\System32\taskkill /im CANMSEngine.exe /f /t
c:\Windows\System32\taskkill /im CANBUS~1.exe /f /t
c:\Windows\System32\taskkill /im CANBUS.exe /f /t
c:\Windows\System32\taskkill /im GSE.exe /f /t
c:\Windows\System32\taskkill /im GantryWCFSelfHostedServices.exe /f /t
c:\Windows\System32\taskkill /im GantryServices.exe /f /t
c:\Windows\System32\taskkill /im GantryLoggerServiceHost.exe /f /t
c:\Windows\System32\taskkill /im GantrySimulator.exe /f /t
c:\Windows\System32\taskkill /im PETMS.exe /f /t
c:\Windows\System32\taskkill /im MSFTest.exe /f /t
c:\Windows\System32\taskkill /im Workflow.exe /f /t
c:\Windows\System32\taskkill /im ExamApplication.exe /f /t
c:\Windows\System32\taskkill /im WINWORD.exe /f /t
c:\Windows\System32\taskkill /im TestExecute.exe /f /t
c:\Windows\System32\taskkill /im TestComplete.exe /f /t
c:\Windows\System32\taskkill /im Easy.exe /f /t
c:\Windows\System32\taskkill /im ReportEditor.exe /f /t
c:\Windows\System32\taskkill /im FilmViewApp.exe /f /t
c:\Windows\System32\taskkill /im PrintingServer.exe /f /t
c:\Windows\System32\taskkill /im ScannerFrameworkWinApp.exe /f /t
c:\Windows\System32\taskkill /im ReconServer.exe /f /t
c:\Windows\System32\taskkill /im ResultsEngineExe.exe /f /t
c:\Windows\System32\taskkill /im PatientDirectory.exe /f /t
c:\Windows\System32\taskkill /im Home.exe /f /t
c:\Windows\System32\taskkill /im nunit-console.exe /f /t
c:\Windows\System32\taskkill /im nunit-agent.exe /f /t
c:\Windows\System32\taskkill /im LogViewer.exe /f /t
c:\Windows\System32\taskkill /im simulators.exe /f /t
c:\Windows\System32\taskkill /im simulatorEngine.exe /f /t
c:\Windows\System32\taskkill /im canBusSimulator.exe /f /t
c:\Windows\System32\taskkill /im LoggerServer.exe /f /t
c:\Windows\System32\taskkill /im CanTraceServer.exe /f /t
c:\Windows\System32\taskkill /im TubeHistoryServer.exe /f /t
c:\Windows\System32\taskkill /im ecgonline.exe /f /t
c:\Windows\System32\taskkill /im Service.Infrastructure.ServiceManager.CTServiceManager.exe /f /t
c:\Windows\System32\taskkill /im Service.Infrastructure.CTServiceHostingApp.exe /f /t
c:\Windows\System32\taskkill /im DW20.exe /f /t
c:\Windows\System32\taskkill /im BugRepViewer.exe /f /t
c:\Windows\System32\taskkill /im BugRep.BugRepCollector.exe /f /t
c:\Windows\System32\taskkill /im PetPro.HostBridge.exe /f /t
c:\Windows\System32\taskkill /im PetPro.PetProMultiHostService.exe /f /t
c:\Windows\System32\taskkill /im PetPro.HostBridgeSimulator.exe /f /t
c:\Windows\System32\taskkill /im PetPro.PetProLogViewerEx.exe /f /t
 
PING 127.0.0.1 -n 5
 
REM ===================== starting register gantry servers =============================
 
call C:\usr\diamond.root\bin\gantryservers\RegisterGS.bat /a
 
 
REM ===================== starting register gantry servers =============================
 
net start PmsRemotingService
net start LoggerService
net start PmsMessageService
net start PmsPrintingService
net start GantryLoggerHost
 
C:\usr\diamond.root\bin\gantryservers\GantryWCFSelfHostedServices.exe