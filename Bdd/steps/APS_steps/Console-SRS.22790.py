"""Step definition skeleton for Console-SRS.22790."""

from behave import given, then, when


class PendingAutomationError(RuntimeError):
    """Marks a Step that still needs an automation implementation."""


_PENDING_MESSAGE = "Pending automation implementation."


def _pending():
    raise PendingAutomationError(_PENDING_MESSAGE)


@given("a patient is registered on the Console")
def given_patient_is_registered(context):
    _pending()


@given('the "Step & Shoot" protocol is selected')
def given_step_and_shoot_protocol_is_selected(context):
    _pending()


@given('the cardiac phase mode is set to "{cardiac_phase_mode}"')
def given_cardiac_phase_mode_is_set(context, cardiac_phase_mode):
    _pending()


@when('the phase tolerance is set to "{phase_tolerance}"')
def when_phase_tolerance_is_set(context, phase_tolerance):
    _pending()


@then('the "Precise Phase" automatic cardiac phase determination reconstruction option is available')
def then_precise_phase_is_available(context):
    _pending()


@then('the "precise phase" automatic heart phase determination reconstruction option is unavailable')
def then_precise_phase_is_unavailable(context):
    _pending()