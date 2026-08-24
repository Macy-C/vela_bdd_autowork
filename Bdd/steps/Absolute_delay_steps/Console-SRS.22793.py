from behave import *
from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.plan.page import PlanPage
from autowork_core.page import get_page
from time import sleep


class PendingAutomationError(RuntimeError):
    """Marks a Step that still needs Recorder generation."""


# Background ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@given('a patient is registered on the Host')
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
# Background ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


#  Scenario: Absolute-delay-based gated acquisition can be configured in Step & Shoot mode ----------
@when('the cardiac phase mode configuration is displayed on the Display Interface')
def when_display_interface_displays_cardiac_phase_mode(context):
    pass


@then('the available cardiac phase mode options are "Relative" and "Absolute"')
def then_display_interface_displays_cardiac_phase_mode_options(context):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    parameters.assert_visible('$absolute_button')
    parameters.assert_visible('$relative_button')


@then('"Relative" is selected as the default cardiac phase mode')
def then_display_interface_displays_cardiac_phase_mode(context):
    plan = get_page(context, PlanPage)
    plan.all_parameters.assert_text_equal('$relative_phase_unit', '%')


#  Scenario: Absolute-delay-based gated acquisition can be configured in Step & Shoot mode ----------



#  Scenario Outline: Phase and phase tolerance units follow the selected cardiac phase mode -----------
@when('the cardiac phase mode is set to "{cardiac_phase_mode}" on the Display Interface')
def when_display_interface_displays_cardiac_phase_mode(context,cardiac_phase_mode):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    parameters.click('$scroll_bar')
    parameters.scroll_to(target='$scroll_bar')
    if cardiac_phase_mode in ('relative', 'Relative'):
        parameters.click('$relative_button')
    else:
        parameters.click('$absolute_button')

@then('the phase unit shown on the Display Interface is "{phase_unit}"')
def then_display_interface_displays_phase_unit(context, phase_unit):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    if phase_unit == '%':
        parameters.assert_text_equal('$relative_phase_unit', phase_unit)
    else:
        parameters.assert_text_equal('$absolute_phase_unit', phase_unit)


@then('the phase tolerance unit shown on the Display Interface is "{phase_tolerance_unit}"')
def then_display_interface_displays_phase_tolerance_unit(context, phase_tolerance_unit):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    if phase_tolerance_unit == '%':
        parameters.assert_text_equal(
            '$relative_phase_tolerance_unit',
            phase_tolerance_unit,
        )
    else:
        parameters.assert_text_equal(
            '$absolute_phase_tolerance_unit',
            phase_tolerance_unit,
        )
#  Scenario Outline: Phase and phase tolerance units follow the selected cardiac phase mode -----------
