"""Step definition skeleton for Console-SRS.22788."""
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


class PendingAutomationError(RuntimeError):
    """Marks a Step that still needs an automation implementation."""


_PENDING_MESSAGE = "Pending automation implementation."


def _pending():
    raise PendingAutomationError(_PENDING_MESSAGE)


@given("patient information is prepared for a {scan_type} scan")
def given_patient_information_is_prepared(context, scan_type):
    patient = get_page(context, PatientPage)
    plan = get_page(context, PlanPage)

    if scan_type == "Cardiac":
        patient.register_patient_for_coronary_cta()
    elif scan_type == "Step & Shoot":
        patient.register_patient_for_step_and_shoot()
        plan.select_step_and_shoot_ax()
        plan.open_all_parameters()
        parameters = plan.all_parameters
        parameters.click('$All_parameters_tag')
        parameters.scroll_to(target='$scroll_bar', steps=5)
        parameters.input_text('$relative_Phase_tolerance_edit_box', 3)
    else:
        patient.register_patient_for_gated_helical_cta()

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
    if scan_type == 'CTA Gated':
        simulator.start_manual_scan()
    else:
        simulator.start_auto_scan()
    sleep(20)

    simulator.minimize_window('$Simulator_window')
    plan.wait_enabled('$go_scan_button', timeout=20)
    plan.click('$go_scan_button')
    if plan.wait_ready('$Dose_Notification_confirm_button', timeout=5):
        plan.click('$Dose_Notification_confirm_button')

    plan.wait_enabled('$Cancel_scan_button')
    simulator.bring_to_front('$Simulator_window', activate=True)
    sleep(5)
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

@when("the user opens the reconstruction page for the {scan_type} scan")
def when_user_opens_reconstruction_page(context, scan_type):
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
    sleep(2)
    view2.expand_dropdown('$relative_combobox')

@then("the automatic cardiac phase determination reconstruction option is available on the reconstruction page")
def then_automatic_phase_option_is_available(context):
    view2 = get_page(context, View2)
    phase_list = view2.get_text(
        '$relative_phase_list',
        first_only=False,
    )
    if 'Precise Phase' not in phase_list:
        raise Exception('Phase option "Precise Phase" is not available')
