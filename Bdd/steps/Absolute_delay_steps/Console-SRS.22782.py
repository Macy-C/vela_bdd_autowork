from behave import given, then, when

from Bdd.page_obj.switch_screen.page import SwitchScreenPage
from autowork_core.page import get_page
from Bdd.page_obj.exam_card_manager.page import ExamCardManagerPage
from Bdd.page_obj.home.page import HomePage
from Bdd.page_obj.scanner_workflow.page import ScannerWorkflowPage


class PendingAutomationError(RuntimeError):
    """Marks a Step that still needs Recorder generation."""


@given(
    "the Cardiac Step & Shoot configuration page is opened "
    "from Exam Card Manager"
)
def given_cardiac_step_and_shoot_configuration_is_open(context):
    switch_screen = get_page(context, SwitchScreenPage)
    switch_screen.toggle_screen()
    switch_screen.toggle_screen()

    scanner_workflow = get_page(context, ScannerWorkflowPage)
    scanner_workflow.open_home()

    home = get_page(context, HomePage)
    home.wait_until_open()
    home.open_exam_card_manager()

    exam_card_manager = get_page(context, ExamCardManagerPage)
    exam_card_manager.wait_until_open()

    exam_card_manager.exam_card_selection.click('$cardiac_group')
    exam_card_manager.exam_card_selection.click('$step_and_shoot_exam_card')
    exam_card_manager.exam_card_selection.click('$ok_by_name')



@given("a clinical sequence item is selected")
def given_clinical_sequence_item_is_selected(context):
    page = get_page(context, ExamCardManagerPage)
    page.clinical_sequence.select_step_and_shoot_ax()


@when('Scan Type is set to "{scan_type}"')
def when_scan_type_is_set(context, scan_type):
    page = get_page(context, ExamCardManagerPage)
    page.scan_parameters.set_scan_type(scan_type)


@then("the Absolute Delay option should be enabled")
def then_absolute_delay_option_should_be_enabled(context):
    page = get_page(context, ExamCardManagerPage)
    page.scan_parameters.scroll_to("$parameters_scroll","down",16)
    page.scan_parameters.assert_enabled("$absolute_by_name")


@given("a patient is registered with the Coronary CTA protocol")
def given_patient_is_registered_with_coronary_cta(context):
    raise PendingAutomationError(
        "Pending Recorder generation: register a Coronary CTA patient."
    )


@given("the scan and online reconstruction are performed")
def given_scan_and_online_reconstruction_are_performed(context):
    raise PendingAutomationError(
        "Pending Recorder generation: perform scan and online reconstruction."
    )


@when("offline reconstruction is performed based on the current results")
def when_offline_reconstruction_is_performed(context):
    raise PendingAutomationError(
        "Pending Recorder generation: perform offline reconstruction."
    )


@then(
    "the absolute-delay-based cardiac reconstruction option can be selected"
)
def then_absolute_delay_cardiac_reconstruction_can_be_selected(context):
    raise PendingAutomationError(
        "Pending Recorder generation: verify the reconstruction option."
    )