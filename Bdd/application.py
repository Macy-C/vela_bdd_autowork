import os
import subprocess
from pathlib import Path
from time import sleep

from loguru import logger

from autowork_core.page import get_page
from autowork_core.runtime.tag_manager import normalize_tag
from config.settings import settings


BASE_SERVICES = (
    "PmsCT Logger Service",
    "PmsCT Messaging Service",
    "PmsCT Printing Service",
    "PmsCT Remoting Service",
)
GANTRY_APPS = (
    r"C:\usr\diamond.root\bin\gantryservers\CanBusSimulator.exe",
    r"C:\usr\diamond.root\bin\gantryservers\CANMSEngine.exe",
    r"C:\usr\diamond.root\bin\gantryservers\GantryWCFSelfHostedServices.exe",
)
GANTRY_SERVICES = (
    "Gantry Services",
    "GantryLoggerHost",
)
PROCESS_NAMES = (
    "PmsRemotingService.exe",
    "PmsPrintingService.exe",
    "MessageService.exe",
    "LoggerSvc.exe",
    "WatchDogService.exe",
    "PmsWindowsPrinting.exe",
    "CardiacServer.exe",
    "IrsSim.exe",
    "IrsSimUI.exe",
    "LOGGER~1.exe",
    "CANMSE~1.exe",
    "CANMSEngine.exe",
    "CANBUS~1.exe",
    "CANBUS.exe",
    "GSE.exe",
    "GantryWCFSelfHostedServices.exe",
    "GantryServices.exe",
    "GantryLoggerServiceHost.exe",
    "GantrySimulator.exe",
    "PETMS.exe",
    "MSFTest.exe",
    "Workflow.exe",
    "ExamApplication.exe",
    "WINWORD.exe",
    "TestExecute.exe",
    "TestComplete.exe",
    "Easy.exe",
    "ReportEditor.exe",
    "FilmViewApp.exe",
    "PrintingServer.exe",
    "ScannerFrameworkWinApp.exe",
    "ReconServer.exe",
    "ResultsEngineExe.exe",
    "PatientDirectory.exe",
    "Home.exe",
    "nunit-console.exe",
    "nunit-agent.exe",
    "LogViewer.exe",
    "Simulators.exe",
    "SimulatorEngine.exe",
    "CanBusSimulator.exe",
    "LoggerServer.exe",
    "CanTraceServer.exe",
    "TubeHistoryServer.exe",
    "ecgonline.exe",
    "Service.Infrastructure.ServiceManager.CTServiceManager.exe",
    "Service.Infrastructure.CTServiceHostingApp.exe",
    "DW20.exe",
    "BugRepViewer.exe",
    "BugRep.BugRepCollector.exe",
    "PetPro.HostBridge.exe",
    "PetPro.PetProMultiHostService.exe",
    "PetPro.HostBridgeSimulator.exe",
    "PetPro.PetProLogViewerEx.exe",
)
POST_STOP_SERVICES = (
    "PmsRemotingService",
    "LoggerService",
    "PmsMessageService",
    "PmsPrintingService",
    "GantryLoggerHost",
)
PMS_WINDOWS_PRINTING = r"C:\Pms\System\PmsWindowsPrinting.exe"
PRODUCT_LOGON = r"C:\Pms\bin\Product.Logon.Philips_Service.cmd"
SIMULATOR_ENGINE = r"C:\Pms\Simulators\SystemSimulator\Server\SimulatorEngine.exe"
SIMULATORS = r"C:\Pms\Simulators\SystemSimulator\Client\Simulators.exe"
REGISTER_GANTRY_SERVERS = r"C:\usr\diamond.root\bin\gantryservers\RegisterGS.bat"
GANTRY_SERVICE_HOST = GANTRY_APPS[-1]


def _uses_gantry(scenario):
    return "gantry" in {
        normalize_tag(tag)
        for tag in getattr(scenario, "effective_tags", ())
    }


def start_application():
    for service in BASE_SERVICES:
        _run_command(["net.exe", "start", service])

    for app in GANTRY_APPS:
        _start_hidden_file(app)

    sleep(5)
    _start_hidden_file(PMS_WINDOWS_PRINTING)
    _start_hidden_file(PRODUCT_LOGON)


def start_simulator():
    for service in BASE_SERVICES:
        _run_command(["net.exe", "start", service])

    for service in GANTRY_SERVICES:
        _run_command(["net.exe", "start", service])

    for app in GANTRY_APPS:
        _start_hidden_file(app)

    sleep(5)
    _start_hidden_file(SIMULATOR_ENGINE)
    sleep(5)
    _start_file(SIMULATORS)


def stop_application():
    for process_name in PROCESS_NAMES:
        _run_command(["taskkill.exe", "/im", process_name, "/f", "/t"])

    sleep(5)
    _start_hidden_file(REGISTER_GANTRY_SERVERS, "/a")

    for service_name in POST_STOP_SERVICES:
        _run_command(["net.exe", "start", service_name])

    _start_hidden_file(GANTRY_SERVICE_HOST)


def prepare_scenario(context, scenario):
    auto_mode = settings.app_launch_mode != "attach"
    if _uses_gantry(scenario):
        from Bdd.page_obj.simulator.page import SimulatorPage

        if auto_mode:
            sleep(2)
            start_simulator()
        simulator = get_page(context, SimulatorPage)
        context.autowork_scenario.simulator = simulator
        try:
            simulator.initialize(auto_mode=auto_mode, timeout=60)
        except Exception:
            cleanup_scenario(context, scenario)
            raise

    if auto_mode:
        from Bdd.page_obj.patient.page import PatientPage

        patient = get_page(context, PatientPage)
        if not patient.wait_until_open(timeout=30):
            raise TimeoutError(
                "Patient window.yaml did not open within 30 seconds"
            )


def cleanup_scenario(context, scenario):
    state = context.autowork_scenario
    simulator = getattr(state, "simulator", None)
    state.simulator = None
    try:
        if simulator is not None:
            simulator.close()
    except Exception as error:
        logger.warning(f"释放 SimulatorPage 失败: {error}")


def _run_command(command, cwd=None):
    logger.info("> {}", subprocess.list2cmdline(command))
    completed = subprocess.run(
        command,
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
        startupinfo=_hidden_startupinfo(),
    )
    output = (completed.stdout or completed.stderr).strip()
    if output:
        logger.info(output)
    return completed


def _start_file(file_path):
    path = Path(file_path)
    logger.info("> start {}", file_path)
    os.startfile(
        str(path),
        cwd=str(path.parent),
        show_cmd=1,
    )


def _start_hidden_file(file_path, *arguments):
    path = Path(file_path)
    if path.suffix.casefold() not in {".bat", ".cmd"}:
        logger.info("> start hidden {}", file_path)
        os.startfile(
            str(path),
            cwd=str(path.parent),
            show_cmd=subprocess.SW_HIDE,
        )
        return None

    command = ["cmd.exe", "/d", "/c", str(path), *arguments]
    logger.info("> start hidden {}", subprocess.list2cmdline(command))
    process = subprocess.Popen(
        command,
        cwd=str(path.parent),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        startupinfo=_hidden_startupinfo(),
        close_fds=True,
    )
    logger.info("hidden process started pid={}", process.pid)
    return process


def _hidden_startupinfo():
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return startupinfo