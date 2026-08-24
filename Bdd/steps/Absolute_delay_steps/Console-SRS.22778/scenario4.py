"""Step definitions for Console-SRS.22778 scenario 4."""
import re
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
    """Marks a Step that still needs Recorder generation."""


_PENDING_MESSAGE = "Pending Recorder generation."


@given('a patient is registered on the Host')
def given_patient_is_registered_on_host(context):
    patient = get_page(context, PatientPage)
    patient.register_patient_for_coronary_cta()


@given('the "Coronary CTA" protocol is selected')
def given_coronary_cta_protocol_is_selected(context):
    plan = get_page(context, PlanPage)
    plan.right_click('$Locator_locator_2')
    plan.click('$Locator_locator_2_delete')
    sleep(1)

@given('Cardiac DoseRight is not selected')
def given_cardiac_doseright_is_not_selected(context):
    pass


@given('the scan is performed')
def given_scan_is_performed(context):
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


@given('the final reconstruction is started')
def given_final_reconstruction_is_started(context):
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

@given('the reconstruction result is edited in Surview')
def given_reconstruction_result_is_edited_in_surview(context):
    patientD = get_page(context, PatientDirectory)
    patientD.input_text('$Patient_ID_input', patientD.get_variable('patient_id'))
    # patientD.input_text('$Patient_ID_input','00000064')
    patientD.click('$refresh_Button')
    patientD.click('$studies_first_result')

    patientD.input_text('$Series_No_input', '201')
    patientD.click('$Series_first_result')
    patientD.click('$recon_button')
    sleep(5)
    view2 = get_page(context, View2)
    view2.click('$Start_Recon_Button')
    sleep(15)
    view2.click('$Edit_Result_Button',wait_type='enabled')
    view2.click('$Edit_Results_on_Surview_Button')
    sleep(1)
    view2.click('$view2_show_all_button')

@when('"{cardiac_phase_mode}" is selected in Result Parameters')
def when_cardiac_phase_mode_is_selected_in_result_parameters(context, cardiac_phase_mode):
    view2 = get_page(context, View2)
    if cardiac_phase_mode == 'absolute':
        view2.click('$absolute_option')
    else:
        view2.click('$relative_option')


@when('the reconstruction phase value is set to "{recon_phase_value}"')
def when_reconstruction_phase_value_is_set(context, recon_phase_value):
    phase_tolerance_value = re.sub(r"\D", "", recon_phase_value)
    view2 = get_page(context, View2)
    if recon_phase_value.endswith('%'):
        view2.input_text('$relative_editbox',phase_tolerance_value)
    else:
        view2.input_text('$absolute_editbox',phase_tolerance_value)


@when('the reconstruction is performed')
def when_reconstruction_is_performed(context):
    view2 = get_page(context, View2)
    view2.click('$Start_Recon_Button')
    sleep(15)

@then('in the View, the four-corner image information should contain the Relative or Absolute indicator consistent with "{recon_phase_value}" in the Examples table')
def then_view_four_corner_information_should_contain_indicator(context, recon_phase_value):
    view2 = get_page(context, View2)
    view2.assert_ocr_contains(f'ECG: {recon_phase_value}',region='$ExamApplication_window')


@when('Image Parameters is opened')
def when_image_parameters_is_opened(context):
    view2 = get_page(context, View2)
    view2.click('$image_parameters_Button')



@then('in Image Parameters, the Relative or Absolute indicator should be consistent with "{recon_phase_value}" in the Examples table')
def then_image_parameters_indicator_should_be_consistent(context, recon_phase_value):
    view2 = get_page(context, View2)
    image_parameters = view2.image_parameters
    image_parameters.assert_attr_contains('$Series_Description_input','Value.Value',recon_phase_value)
    image_parameters.assert_attr_contains('$Tagging_input','Value.Value',recon_phase_value)
    image_parameters.click('$ok_button')



