import re
from time import sleep
from behave import *
from Bdd.page_obj.home.page import HomePage
from Bdd.page_obj.log_viewer.page import LogViewerPage
from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.plan.page import PlanPage
from Bdd.page_obj.scanner_workflow.page import ScannerWorkflowPage
from Bdd.page_obj.simulator.page import SimulatorPage
from Bdd.page_obj.switch_screen.page import SwitchScreenPage
from autowork_core.page import get_page


#  Scenario Outline: Log Viewer shows configured phase parameters for the Gantry scan request in absolute mode +++++++
@given('a patient is registered on the Console')
def given_patient_is_registered(context):
    patient = get_page(context, PatientPage)
    patient.register_patient_for_step_and_shoot()

@given('the "Step & Shoot" protocol is selected')
def given_select_Step_and_Shoot(context):
    plan = get_page(context, PlanPage)
    plan.select_step_and_shoot_ax()

@given('the clinical sequence parameters are open on the Display Interface')
def given_patient_is_registered(context):
    plan = get_page(context, PlanPage)
    plan.open_all_parameters()

@given('the cardiac phase mode is set to "absolute" on the Display Interface')
def when_display_interface_displays_cardiac_phase_mode(context):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    parameters.click('$All_parameters_tag')
    parameters.click('$scroll_bar')
    parameters.scroll_to(target='$scroll_bar')
    parameters.click('$absolute_button')

@given('the phase is set to "{phase}" on the Display Interface')
def when_patient_is_registered(context,phase):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase = re.sub(r"\D", "", phase)
    parameters.input_text('$absolute_Phase_edit_box', phase)
    parameters.click('$absolute_Phase_unit_ocr')

@given('the phase tolerance is set to "{phase_tolerance}" on the Display Interface')
def when_phase_tolerance_is_set(context, phase_tolerance):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_tolerance = re.sub(r"\D", "", phase_tolerance)
    parameters.input_text(
        '$absolute_Phase_tolerance_edit_box',
        phase_tolerance,
    )
    parameters.click('$absolute_Phase_unit_ocr')

@when('"GO" is clicked on the Display Interface')
def when_click_go_on_display_interface(context):
    plan = get_page(context, PlanPage)
    simulator = get_page(context, SimulatorPage)

    simulator.unset_window_topmost('$Simulator_window')
    # simulator.bring_to_front('$Simulator_window', activate=True)
    simulator.bring_to_front('$Simulator_window', activate=True)
    if simulator.ensure_ecg_on():
        if plan.wait_visible('$MessageBox_window', timeout=8):
            plan.click('$MessageBox_OK_button')

    simulator.minimize_window('$Simulator_window')
    plan.click('$go_scan_button')
    plan.wait_enabled('$Cancel_scan_button')

    simulator.bring_to_front('$Simulator_window', activate=True)
    if plan.wait_visible('$MessageBox_window', timeout=5):
        plan.click('$MessageBox_OK_button')
    simulator.wait_ready('$Simulator_window')
    sleep(0.5)
    simulator.start_auto_scan()
    sleep(20)

    simulator.minimize_window('$Simulator_window')
    plan.wait_enabled('$go_scan_button', timeout=20)
    plan.click('$go_scan_button')
    plan.wait_enabled('$Cancel_scan_button')

    simulator.bring_to_front('$Simulator_window', activate=True)
    sleep(0.5)
    simulator.start_manual_scan()

    sleep(3)
    simulator.minimize_window('$Simulator_window')
    sleep(2)
    plan.click('$legacy_scan_transition_position')
    plan.click('$step_and_shoot_Ax')
    sleep(2)

    plan.click('$go_scan_button')
    if plan.wait_ready('$Dose_Notification_confirm_button', timeout=5):
        plan.click('$Dose_Notification_confirm_button')
        plan.click('$go_scan_button')
    plan.wait_enabled('$Cancel_scan_button')

    simulator.bring_to_front('$Simulator_window', activate=True)
    sleep(0.5)
    simulator.start_auto_scan(wait_type="exists")
    sleep(3)

    simulator.minimize_window('$Simulator_window')
    plan.click('$start_scan_button')
    sleep(1)
    simulator.minimize_window('$Simulator_window')
    sleep(5)

@step('the Log Viewer shows a Console-to-Gantry scan parameter log')
def then_log_viewer_shows_console_to_gantry_scan_parameter_log(context):
    sleep(10)

    switch_screen = get_page(context, SwitchScreenPage)
    switch_screen.toggle_screen()
    switch_screen.toggle_screen()

    scanner_workflow = get_page(context, ScannerWorkflowPage)
    scanner_workflow.open_home()

    home = get_page(context, HomePage)
    home.click('$Log_Viewer_button')
    sleep(3)
    log_viewer = get_page(context, LogViewerPage)
    log_viewer.click('$existing_log_view1_maximize_button')
    log_viewer.click('$TextMessage_edit_box')
    log_viewer.input_text(
        '$TextMessage_edit_box',
        'CardiacPulmoDevice : CRTC: '
        'Cardiac device sent Axial params to CRTC',
    )
    log_viewer.double_click('$last_TextMessage_edit_box')

@then('the log shows phase "{phase}"')
def then_log_shows_phase(context, phase):
    log_viewer = get_page(context, LogViewerPage)
    log_viewer.assert_attr_contains(
        '$Message_Text_res_box',
        'Value.Value',
        f'phase: {phase}',
    )

@then('the log shows phase tolerance "{phase_tolerance}"')
def then_log_shows_phase_tolerance(context, phase_tolerance):
    log_viewer = get_page(context, LogViewerPage)
    log_viewer.assert_attr_contains(
        '$Message_Text_res_box',
        'Value.Value',
        f'tolerance: {phase_tolerance}',
    )

@then('the log shows PhaseMode "{PhaseMode}"')
def then_log_shows_phase_mode(context, PhaseMode):
    log_viewer = get_page(context, LogViewerPage)
    log_viewer.assert_attr_contains(
        '$Message_Text_res_box',
        'Value.Value',
        f'PhaseMode: {PhaseMode}',
    )
#  Scenario Outline: Log Viewer shows configured phase parameters for the Gantry scan request in absolute mode +++++++
