"""Step definition skeleton for Console-SRS.22789."""
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


@given("a patient is registered on the Console")
def given_patient_is_registered(context):
    patient = get_page(context, PatientPage)
    patient.register_patient_for_step_and_shoot()

@given('the "Step & Shoot" protocol is selected')
def given_step_and_shoot_protocol_is_selected(context):
    plan = get_page(context, PlanPage)
    plan.select_step_and_shoot_ax()
    plan.open_all_parameters()
    parameters = plan.all_parameters
    parameters.scroll_to(target='$scroll_bar',steps=5)


@when('the user selects "Full Coverage, Longer Cycle Time"')
def when_user_selects_longer_cycle_time(context):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    parameters.click('$Full_coverage_longer_cycle_time_option')
    parameters.click('$Proceed_button')
    parameters.expand_dropdown('$4_1_phase_combobox')


@then('the "Precise Phase" automatic cardiac phase determination reconstruction option is unavailable')
def then_precise_phase_is_unavailable(context):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_list = parameters.get_text(
        '$relative_phase_list',
        first_only=False,
    )
    if 'Precise Phase' in phase_list:
        raise Exception('Phase option "Precise Phase" is not available')


@when("the user opens offline reconstruction for the Step & Shoot acquisition")
def when_user_opens_offline_reconstruction(context):
    plan = get_page(context, PlanPage)
    plan.open_all_parameters()
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
    sleep(6)

    warning = get_page(context, WarningPage)
    if warning.wait_until_open():
        warning.click('$warning_ok_button')

    switch_screen = get_page(context, SwitchScreenPage)
    switch_screen.toggle_screen()

@then('the "Precise Phase" automatic cardiac phase determination reconstruction option is unavailable in offline reconstruction')
def then_precise_phase_is_unavailable_offline(context):
    patientD = get_page(context, PatientDirectory)
    patientD.input_text('$Patient_ID_input', patientD.get_variable('patient_id'))
    # patientD.input_text('$Patient_ID_input', '00000180')
    patientD.click('$refresh_Button')
    patientD.click('$studies_first_result')

    patientD.input_text('$Series_No_input', '201')
    patientD.click('$Series_first_result')
    patientD.click('$recon_button')
    sleep(5)
    view2 = get_page(context, View2)
    view2.click('$view2_show_all_button')
    sleep(2)
    view2.expand_dropdown('$relative_combobox')


    view2 = get_page(context, View2)
    phase_list = view2.get_text(
        '$relative_phase_list',
        first_only=False,
    )
    if 'Precise Phase' in phase_list:
        raise Exception('Phase option "{o}" is not available')