"""Step definitions for Console-SRS.22778 scenario 1."""
import re
from time import sleep
from behave import given, then, when
from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.patient_directory.page import PatientDirectory
from Bdd.page_obj.plan.page import PlanPage
from Bdd.page_obj.scanner_workflow import ScannerWorkflowPage
from Bdd.page_obj.simulator.page import SimulatorPage
from Bdd.page_obj.switch_screen.page import SwitchScreenPage
from Bdd.page_obj.view2.image_parameters import ImageParameters
from Bdd.page_obj.view2.view2 import View2
from Bdd.page_obj.warning.page import WarningPage
from autowork_core.page import get_page


class PendingAutomationError(RuntimeError):
    """Marks a Step that still needs Recorder generation."""


_PENDING_MESSAGE = "Pending Recorder generation."


@given('a patient is registered on the Host')
def given_patient_is_registered_on_host(context):
    patient = get_page(context, PatientPage)
    patient.register_patient_for_step_and_shoot()


@given('a Step & Shoot cardiac scan is planned with the "{cardiac_phase_mode}" cardiac phase mode')
def given_step_and_shoot_cardiac_scan_is_planned(context, cardiac_phase_mode):
    plan = get_page(context, PlanPage)

    plan.right_click('$Locator_locator_2')
    plan.click('$Locator_locator_2_delete')
    sleep(2)
    plan.select_step_and_shoot_ax()
    plan.open_all_parameters()
    parameters = plan.all_parameters
    parameters.click('$All_parameters_tag')
    # parameters.click('$scroll_bar')
    parameters.scroll_to(target='$scroll_bar')
    if cardiac_phase_mode == 'absolute':
        parameters.click('$absolute_button')

@given('the scan phase is configured as "{scan_phase_value}"')
def given_scan_phase_is_configured(context, scan_phase_value):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_value = re.sub(r"\D", "", scan_phase_value)
    if scan_phase_value.endswith('%'):
        parameters.input_text('$relative_Phase_edit_box', phase_value)
        parameters.click('$relative_Phase_unit_ocr')
    else:
        parameters.input_text('$absolute_Phase_edit_box', phase_value)
        parameters.click('$absolute_Phase_unit_ocr')

@given('the scan phase tolerance is configured as "{scan_phase_tolerance_value}"')
def given_scan_phase_tolerance_is_configured(context, scan_phase_tolerance_value):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_tolerance_value = re.sub(r"\D", "", scan_phase_tolerance_value)
    if scan_phase_tolerance_value.endswith('%'):
        parameters.input_text(
            '$relative_Phase_tolerance_edit_box',
            phase_tolerance_value,
        )
        parameters.click('$relative_Phase_tolerance_unit_ocr')
    else:
        parameters.input_text(
            '$absolute_Phase_tolerance_edit_box',
            phase_tolerance_value,
        )
        parameters.click('$absolute_Phase_tolerance_unit_ocr')


@given('the Step & Shoot scan is performed')
def given_step_and_shoot_scan_is_performed(context):
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

@when('the final reconstruction is started for use "{recon_phase_value}"')
def when_final_reconstruction_is_started(context,recon_phase_value):
    patientD = get_page(context, PatientDirectory)
    patientD.input_text('$Patient_ID_input', patientD.get_variable('patient_id'))
    # patientD.input_text('$Patient_ID_input','00000048')
    patientD.click('$studies_first_result')

    patientD.input_text('$Series_No_input', '201')
    patientD.click('$Series_first_result')
    patientD.click('$recon_button')
    sleep(5)

    view2 = get_page(context, View2)
    view2.click('$view2_show_all_button')

    phase_tolerance_value = re.sub(r"\D", "", recon_phase_value)
    if recon_phase_value.endswith('%'):
        view2.input_text('$relative_editbox',phase_tolerance_value)
    else:
        view2.input_text('$absolute_editbox',phase_tolerance_value)

    view2.click('$Start_Recon_Button')
    sleep(15)

@then('in the View, the four-corner image information should contain the Relative or Absolute indicator consistent with "{recon_phase_value}" in the Examples table')
def then_view_four_corner_information_should_contain_indicator(context, recon_phase_value):
    view2 = get_page(context, View2)
    view2.assert_ocr_contains(f'ECG: {recon_phase_value}',region='$ExamApplication_window')

@then('in Image Parameters, the Relative or Absolute indicator should be consistent with "{recon_phase_value}" in the Examples table')
def then_image_parameters_indicator_should_be_consistent(context, recon_phase_value):
    view2 = get_page(context, View2)
    image_parameters = view2.image_parameters
    view2.click('$image_parameters_Button')
    image_parameters.assert_attr_contains('$Series_Description_input','Value.Value',recon_phase_value)
    image_parameters.assert_attr_contains('$Gating_input','Value.Value',recon_phase_value)
    image_parameters.click('$ok_button')

@when('the reconstruction result is edited in Surview')
def when_reconstruction_result_is_edited_in_surview(context):
    view2 = get_page(context, View2)
    view2.click('$Edit_Result_Button',wait_type='enabled')
    view2.click('$Edit_Results_on_Surview_Button')
    sleep(1)
    view2.click('$Start_Recon_Button')
    sleep(15)


@then('in the View, the Relative or Absolute indicator should be consistent with "{recon_phase_value}" in the Examples table')
def then_view_indicator_should_be_consistent(context, recon_phase_value):
    view2 = get_page(context, View2)
    view2.assert_ocr_contains(f'ECG: {recon_phase_value}',region='$ExamApplication_window')
