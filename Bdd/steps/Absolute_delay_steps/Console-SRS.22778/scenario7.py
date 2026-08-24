"""Step definitions for Console-SRS.22778 scenario 7."""

from time import sleep

from behave import given, then, when

from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.patient_directory.page import PatientDirectory
from Bdd.page_obj.patient_directory.quick_review import QuickReviewPage
from Bdd.page_obj.plan.page import PlanPage
from Bdd.page_obj.review.page import ReviewPage
from Bdd.page_obj.scanner_workflow import ScannerWorkflowPage
from Bdd.page_obj.simulator.page import SimulatorPage
from Bdd.page_obj.switch_screen.page import SwitchScreenPage
from Bdd.page_obj.view2.view2 import View2
from Bdd.page_obj.warning.page import WarningPage
from autowork_core.page import get_page

class PendingAutomationError(RuntimeError):
    """Marks a Step that still needs Recorder generation."""


_PENDING_MESSAGE = "Pending Recorder generation."


@given('reconstructed image data is prepared from Step & Shoot and Helical scans')
def given_reconstructed_image_data_is_prepared(context):
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
    sleep(9)

    warning = get_page(context, WarningPage)
    if warning.wait_until_open():
        warning.click('$warning_ok_button')

    switch_screen = get_page(context, SwitchScreenPage)
    switch_screen.toggle_screen()

@given('the reconstructed image is generated with the "{cardiac_phase_mode}" option')
def given_reconstructed_image_is_generated_with_option(context, cardiac_phase_mode):
    patientD = get_page(context, PatientDirectory)
    patientD.input_text('$Patient_ID_input', patientD.get_variable('patient_id'))
    patientD.click('$studies_first_result')

    patientD.input_text('$Series_No_input', '201')
    patientD.click('$Series_first_result')
    patientD.click('$recon_button')
    sleep(5)
    view2 = get_page(context, View2)
    view2.click('$view2_show_all_button')
    phase = None
    if cardiac_phase_mode == 'absolute':
        phase = '300'
        view2.click('$absolute_option')
        view2.input_text('$absolute_editbox',phase)
    else:
        phase = '70'
        view2.click('$relative_option')
        view2.input_text('$relative_editbox',phase)
    view2.set_variable('phase',phase) #set phase
    view2.click('$Start_Recon_Button')
    sleep(15)
    view2.click('$Exit_Button')

@when('the Quick Review screen is opened')
def when_quick_review_screen_is_opened(context):
    patientD = get_page(context, PatientDirectory)
    patientD.input_text('$Patient_ID_input', patientD.get_variable('patient_id'))
    # patientD.input_text('$Patient_ID_input', '00000094')
    patientD.click('$studies_first_result')
    patientD.input_text('$Series_No_input', '203')
    patientD.click('$Series_first_result')
    patientD.click('$quick_review_button')
    sleep(3)

@then('in Quick Review,the ECG value in the four-corner information should contain the value range "{phase_scope}" from the Examples table')
def then_quick_review_ecg_value_should_contain_value_range(context, phase_scope):
    print('next to cover')


@then('in Quick Review,the ECG value in the four-corner information should contain the value unit "{phase_unit}" from the Examples table')
def then_quick_review_ecg_value_should_contain_value_unit(context, phase_unit):
    patientD = get_page(context, PatientDirectory)
    quick_review = patientD.quick_review
    phase = quick_review.get_variable('phase')
    quick_review.assert_ocr_contains(f'ECG: {phase+phase_unit}',region='$quick_review_imaging')


@when('Image Parameters is opened from the Quick Review screen')
def when_image_parameters_is_opened_from_quick_review_screen(context):
    patientD = get_page(context, PatientDirectory)
    quick_review = patientD.quick_review
    quick_review.click('$Image_info_Button')


@then('Tagging should contain the value range "{phase_scope}" from the Examples table')
def then_tagging_should_contain_value_range(context, phase_scope):
    print('next to cover')


@then('Tagging should contain the value unit "{phase_unit}" from the Examples table')
def then_tagging_should_contain_value_unit(context, phase_unit):
    patientD = get_page(context, PatientDirectory)
    quick_review = patientD.quick_review
    phase = quick_review.get_variable('phase')
    quick_review.assert_attr_contains('$Series_Description_input','Value.Value',phase+phase_unit)
