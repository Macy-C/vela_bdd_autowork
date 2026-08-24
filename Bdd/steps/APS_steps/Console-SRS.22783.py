"""Step definition skeleton for Console-SRS.22783."""
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


@given("a cardiac examination is configured with a helical cardiac acquisition")
def given_helical_cardiac_acquisition_is_configured(context):
    patient = get_page(context, PatientPage)
    plan = get_page(context, PlanPage)

    patient.register_patient_for_coronary_cta()
    plan.click('$Cardiac_Helical_4_1')
    plan.open_all_parameters()

    parameters = plan.all_parameters
    parameters.click('$All_parameters_tag')


@when("the user opens the automatic cardiac phase determination reconstruction options")
def when_user_opens_automatic_phase_options(context):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    parameters.expand_dropdown('$4_1_phase_combobox')


@then("the Console provides the following automatic cardiac phase determination reconstruction options:")
def then_console_provides_automatic_phase_options(context):
    rows = [row.as_dict() for row in context.table]
    option = [row['option'] for row in rows]

    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_list = parameters.get_text(
        '$4_1_phase_list',
        first_only=False,
    )
    for o in option:
        if o not in phase_list:
            raise Exception('Phase option "{o}" is not available'.format(o=o))
    # if rows[0]['option'] not in phase_list or rows[1]['option'] not in phase_list or rows[2]['option'] not in phase_list:


@given("a completed helical cardiac acquisition is available for reconstruction")
def given_completed_helical_acquisition_is_available(context):
    patient = get_page(context, PatientPage)
    patient.register_patient_for_coronary_cta()
    plan = get_page(context, PlanPage)
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

@when('the user selects reconstruction_option and starts reconstruction')
@when('the user selects "Precise Phase" and starts reconstruction')
def when_user_selects_option_and_starts_reconstruction(context):
    patientD = get_page(context, PatientDirectory)
    patientD.input_text('$Patient_ID_input', patientD.get_variable('patient_id'))
    # patientD.input_text('$Patient_ID_input', '00000093')
    patientD.click('$studies_first_result')

    patientD.input_text('$Series_No_input', '201')
    patientD.click('$Series_first_result')
    patientD.click('$recon_button')
    sleep(5)
    view2 = get_page(context, View2)
    view2.click('$view2_show_all_button')
    sleep(2)
    view2.expand_dropdown('$relative_combobox')

@then("the reconstructed images are available for review")
def then_reconstructed_images_are_available(context):
    rows = [row.as_dict() for row in context.table]
    option = [row['option'] for row in rows]

    view2 = get_page(context, View2)
    phase_list = view2.get_text(
        '$relative_phase_list',
        first_only=False,
    )
    for o in option:
        if o not in phase_list:
            raise Exception('Phase option "{o}" is not available'.format(o=o))
    # if rows[0]['option'] not in phase_list or rows[1]['option'] not in phase_list or rows[2]['option'] not in phase_list:



@given("a cardiac examination is configured with a Step & Shoot cardiac acquisition")
def given_step_and_shoot_cardiac_acquisition_is_configured(context):
    patient = get_page(context, PatientPage)
    patient.register_patient_for_step_and_shoot()
    plan = get_page(context, PlanPage)
    plan.select_step_and_shoot_ax()
    plan.open_all_parameters()
    parameters = plan.all_parameters
    parameters.click('$All_parameters_tag')
    parameters.scroll_to(target='$scroll_bar',steps=5)
    parameters.input_text('$relative_Phase_tolerance_edit_box',3)
    parameters.click('$step_and_shoot_4_1')
    parameters.expand_dropdown('$4_1_phase_combobox')


@then("the Console provides only the following automatic cardiac phase determination reconstruction option:")
def then_console_provides_only_supported_automatic_phase_option(context):
    rows = [row.as_dict() for row in context.table]
    option = [row['option'] for row in rows]

    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_list = parameters.get_text(
        '$4_1_phase_list',
        first_only=False,
    )
    for o in option:
        if o not in phase_list:
            raise Exception('Phase option "{o}" is not available'.format(o=o))
    # if rows[0]['option'] not in phase_list or rows[1]['option'] not in phase_list or rows[2]['option'] not in phase_list:


@given("a completed Step & Shoot cardiac acquisition is available for reconstruction")
def given_completed_step_and_shoot_acquisition_is_available(context):
    patient = get_page(context, PatientPage)
    patient.register_patient_for_step_and_shoot()
    plan = get_page(context, PlanPage)
    plan.select_step_and_shoot_ax()
    plan.open_all_parameters()
    parameters = plan.all_parameters
    parameters.click('$All_parameters_tag')
    parameters.scroll_to(target='$scroll_bar', steps=5)
    parameters.input_text('$relative_Phase_tolerance_edit_box', 3)

    plan.right_click('$Locator_locator_2')
    plan.click('$Locator_locator_2_delete')
    sleep(2)
    parameters = plan.all_parameters
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
    if plan.wait_ready('$Dose_Notification_confirm_button', timeout=5):
        plan.click('$Dose_Notification_confirm_button')

    plan.wait_enabled('$Cancel_scan_button')
    simulator.bring_to_front('$Simulator_window', activate=True)
    sleep(3)
    simulator.start_auto_scan()
    sleep(20)
    simulator.minimize_window('$Simulator_window')

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