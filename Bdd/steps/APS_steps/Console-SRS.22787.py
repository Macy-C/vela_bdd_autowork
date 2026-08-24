"""Step definition skeleton for Console-SRS.22787."""

from pathlib import Path
from time import sleep

from behave import given, then, when

from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.patient_directory.page import PatientDirectory
from Bdd.page_obj.plan.page import PlanPage
from Bdd.page_obj.scanner_workflow import ScannerWorkflowPage
from Bdd.page_obj.simulator.page import SimulatorPage
from Bdd.page_obj.switch_screen.page import SwitchScreenPage
from Bdd.page_obj.view2.view2 import View2
from Bdd.page_obj.warning.page import WarningPage
from autowork_core.page import get_page
from autowork_core.runtime.application_lifecycle import (
    after_app_stop,
    before_app_start,
)


_LICENSE_KEY_PATH = Path(r"C:\pms\config\System\Licensing\key")
_SUPPORTED_LICENSE_KEY = "ad_and_abs_key"
_UNSUPPORTED_LICENSE_KEY = "not_ad_and_abs_key"


class PendingAutomationError(RuntimeError):
    """Marks a Step that still needs an automation implementation."""


_PENDING_MESSAGE = "Pending automation implementation."


def _pending():
    raise PendingAutomationError(_PENDING_MESSAGE)


def _get_license_key(context, key_name):
    value = context.autowork_run.public_data.get(key_name)
    if not isinstance(value, str) or not value:
        raise ValueError(
            f"Bdd/data/public_data.yaml must define a non-empty {key_name!r}"
        )
    return value


def _write_license_key(context, key_name):
    if not _LICENSE_KEY_PATH.is_file():
        raise FileNotFoundError(
            f"License key file does not exist: {_LICENSE_KEY_PATH}"
        )
    expected = _get_license_key(context, key_name)
    _LICENSE_KEY_PATH.write_text(expected, encoding="utf-8")
    actual = _LICENSE_KEY_PATH.read_text(encoding="utf-8")
    if actual != expected:
        raise OSError(
            f"License key file verification failed: {_LICENSE_KEY_PATH}"
        )


@before_app_start(tags="license_without_absolute_delay")
def configure_license_without_precise_phase(context, scenario):
    _write_license_key(context, _UNSUPPORTED_LICENSE_KEY)


@before_app_start(tags="license_with_absolute_delay")
def configure_license_with_precise_phase(context, scenario):
    _write_license_key(context, _SUPPORTED_LICENSE_KEY)


@after_app_stop(tags="license_without_absolute_delay")
@after_app_stop(tags="license_with_absolute_delay")
def restore_license_configuration(context, scenario):
    _write_license_key(context, _SUPPORTED_LICENSE_KEY)


def _assert_license_key(context, key_name):
    expected = _get_license_key(context, key_name)
    actual = _LICENSE_KEY_PATH.read_text(encoding="utf-8")
    if actual != expected:
        raise AssertionError(
            "Unexpected Precise Phase license key content: "
            f"expected public_data key={key_name!r}"
        )


@given("a supported Precise Phase license key is used")
def given_supported_precise_phase_license_is_used(context):
    _assert_license_key(context, _SUPPORTED_LICENSE_KEY)


@when("the user opens Preferences")
def when_user_opens_preferences(context):
    pat_directory = get_page(context, PatientDirectory)
    switch_screen = get_page(context, SwitchScreenPage)

    switch_screen.toggle_screen()
    pat_directory.open_preferences_window()
    pat_directory.preferences.scroll_the_title_bar()
    sleep(1)
    pat_directory.preferences.open_licensing()
    pat_directory.preferences.scroll_the_license_list()


@then('the License Type field displays "Permanent"')
def then_license_type_displays_permanent(context):
    pat_directory = get_page(context, PatientDirectory)
    pat_directory.preferences.Precise_Phase_license_type_is_Permanent()


@given("a supported Precise Phase license key is not used")
def given_supported_precise_phase_license_is_not_used(context):
    _assert_license_key(context, _UNSUPPORTED_LICENSE_KEY)


@then("the License Type field is empty")
def then_license_type_is_empty(context):
    pat_directory = get_page(context, PatientDirectory)
    pat_directory.preferences.Precise_Phase_license_type_is_None()






@given("a supported cardiac acquisition is configured")
def given_supported_cardiac_acquisition_is_configured(context):
    patient = get_page(context, PatientPage)
    plan = get_page(context, PlanPage)

    patient.register_patient_for_coronary_cta()
    plan.click('$Cardiac_Helical_4_1')
    plan.open_all_parameters()

    parameters = plan.all_parameters
    parameters.click('$All_parameters_tag')
    parameters = plan.all_parameters
    # parameters.expand_dropdown('$4_1_phase_combobox')
    parameters.select_dropdown_option('$4_1_phase_combobox','Precise Phase')

@when("the user starts the scan")
def when_user_starts_scan(context):
    plan = get_page(context, PlanPage)
    plan.click('$go_scan_button')

@then("the Console starts the scan successfully")
def then_console_starts_scan_successfully(context):
    plan = get_page(context, PlanPage)
    plan.assert_disabled('$go_scan_button', timeout=5)

@given("a completed supported cardiac acquisition is available for reconstruction")
def given_completed_supported_acquisition_is_available(context):
    patient = get_page(context, PatientPage)
    plan = get_page(context, PlanPage)

    patient.register_patient_for_coronary_cta()
    plan.right_click('$Locator_locator_2')
    plan.click('$Locator_locator_2_delete')
    sleep(1)

    # scon -----------------------------------------------------------------
    plan = get_page(context, PlanPage)
    simulator = get_page(context, SimulatorPage)

    simulator.bring_to_front('$Simulator_window', activate=True)
    if simulator.ensure_ecg_on():
        if plan.wait_visible('$MessageBox_window', timeout=8):
            plan.click('$MessageBox_OK_button')

    simulator.minimize_window('$Simulator_window')
    plan.click('$go_scan_button')
    plan.wait_enabled('$Cancel_scan_button')

    simulator.bring_to_front('$Simulator_window', activate=True)
    simulator.wait_ready('$Simulator_window')
    sleep(2)
    simulator.start_auto_scan()
    sleep(20)

    simulator.minimize_window('$Simulator_window')
    plan.wait_enabled('$go_scan_button', timeout=20)
    plan.click('$go_scan_button')

    plan.wait_enabled('$Cancel_scan_button')
    simulator.bring_to_front('$Simulator_window', activate=True)
    sleep(3)
    simulator.start_auto_scan()
    sleep(20)
    simulator.minimize_window('$Simulator_window')
    # scon -----------------------------------------------------------------

    plan = get_page(context, PlanPage)
    plan.acquisition.click('$start_final_recon_button')
    scanwf = get_page(context, ScannerWorkflowPage)
    scanwf.wait_enabled('$view_button', timeout=20)

    sleep(2)
    scanwf.click('$endExam_button')
    sleep(9)

    warning = get_page(context, WarningPage)
    if warning.wait_until_open():
        warning.click('$warning_ok_button')

    switch_screen = get_page(context, SwitchScreenPage)
    switch_screen.toggle_screen()

@when("the user starts reconstruction using a Precise Phase option")
def when_user_starts_precise_phase_reconstruction(context):
    patientD = get_page(context, PatientDirectory)
    patientD.input_text('$Patient_ID_input', patientD.get_variable('patient_id'))
    # patientD.input_text('$Patient_ID_input','00000064')
    patientD.click('$studies_first_result')

    patientD.input_text('$Series_No_input', '201')
    patientD.click('$Series_first_result')
    patientD.click('$recon_button')
    sleep(5)
    view2 = get_page(context, View2)
    view2.click('$view2_show_all_button')

    view2.input_text('$relative_editbox','Precise Phase')

    view2.click('$Start_Recon_Button')
    sleep(15)

@then("the Console starts the reconstruction successfully")
def then_console_starts_reconstruction_successfully(context):
    view2 = get_page(context, View2)
    view2.assert_ocr_contains(f'ECG: Precise Phase',region='$ExamApplication_window')
