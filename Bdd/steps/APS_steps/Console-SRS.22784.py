"""Step definition skeleton for Console-SRS.22784."""
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


@given('a completed "{acquisition_type}" cardiac acquisition is available for reconstruction')
def given_completed_acquisition_is_available(context, acquisition_type):
    patient = get_page(context, PatientPage)
    plan = get_page(context, PlanPage)
    plan.set_variable('acquisition_type',acquisition_type)
    if acquisition_type == 'Helical':
        patient.register_patient_for_coronary_cta()
    else:
        patient.register_patient_for_step_and_shoot()
        plan.select_step_and_shoot_ax()
        plan.open_all_parameters()
        parameters = plan.all_parameters
        parameters.click('$All_parameters_tag')
        parameters.scroll_to(target='$scroll_bar', steps=5)
        parameters.input_text('$relative_Phase_tolerance_edit_box', 3)

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
    if plan.wait_ready('$Dose_Notification_confirm_button', timeout=5):
        plan.click('$Dose_Notification_confirm_button')

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

@when('the user reconstructs the acquisition using automatic cardiac phase determination option "{reconstruction_option}"')
def when_user_reconstructs_with_automatic_phase_option(context,reconstruction_option,):
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

    view2.input_text('$relative_editbox',reconstruction_option)

    view2.click('$Start_Recon_Button')
    sleep(15)

@then('the generated image data indicates that automatic cardiac phase determination option "{reconstruction_option}" was used')
def then_generated_image_data_identifies_option(
        context,
        reconstruction_option,
):
    view2 = get_page(context, View2)
    view2.assert_ocr_contains(f'ECG: {reconstruction_option}',region='$ExamApplication_window')

@then('the image paramenters fields accurately identify "{reconstruction_option}" as the automatic cardiac phase determination option used')
def then_image_parameters_identify_option(context, reconstruction_option):
    view2 = get_page(context, View2)
    view2.click('$image_parameters_Button')
    image_parameters = view2.image_parameters
    image_parameters.assert_attr_contains('$Series_Description_input','Value.Value',reconstruction_option)
    if image_parameters.get_variable('acquisition_type') == 'Step & Shoot':
        image_parameters.assert_attr_contains('$Gating_input', 'Value.Value', reconstruction_option)
    else:
        image_parameters.assert_attr_contains('$Tagging_input','Value.Value',reconstruction_option)
    image_parameters.click('$ok_button')