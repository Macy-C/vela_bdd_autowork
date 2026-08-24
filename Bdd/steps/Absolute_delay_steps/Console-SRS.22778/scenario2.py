"""Step definitions for Console-SRS.22778 scenario 2."""
from time import sleep

from behave import given, then, when

from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.plan.page import PlanPage
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

    plan.click('$Cardiac_Helical')
    plan.click('$show_all_button')



@given('Cardiac DoseRight is not selected')
def given_cardiac_doseright_is_not_selected(context):
    pass


@when('the reconstruction sequence parameters dialog is opened')
def when_reconstruction_sequence_parameters_dialog_is_opened(context):
    pass


@then('the absolute cardiac phase configuration option should not be displayed')
def then_absolute_cardiac_phase_configuration_option_should_not_be_displayed(context):
    plan = get_page(context, PlanPage)
    plan.all_parameters.assert_ocr_not_contains('Phase Tolerance',region='$all_parameters_window')
