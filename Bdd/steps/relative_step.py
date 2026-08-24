import re

from behave import *
from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.plan.page import PlanPage
from autowork_core.page import get_page


# Background ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@given('a patient is registered on the console')
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

# Scenario Outline: Parameter ranges and initial values follow the selected cardiac phase mode ------------
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

@then('the initial phase value shown on the Display Interface is "{initial_phase_value}"')
def then_initial_phase_value(context, initial_phase_value):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    if initial_phase_value == '78%':
        parameters.assert_text_equal('$relative_Phase_edit_box', '78')
    elif initial_phase_value == '350 ms':
        parameters.assert_text_equal('$absolute_Phase_edit_box', '350')
    else:
        raise Exception('initial_phase_value not is "78%" or "350 ms"')

@then('the phase range shown on the Display Interface is "{phase_range}"')
def then_phase_range(context, phase_range):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    if phase_range == '35% to 85%':
        min_phase_value, max_phase_value = '35', '85'
        parameters.click_ocr_relative(
            '$relative_Phase_unit_ocr',
            direction='left',
            offset=0.1,
        )
        relative_phase_list = parameters.get_text(
            '$relative_phase_list',
            first_only=False,
        )
        if min(relative_phase_list) != min_phase_value:
            raise Exception('min_phase_value is not "35"')
        if max(relative_phase_list) != max_phase_value:
            raise Exception('max_phase_value is not "85"')
        parameters.click_ocr_relative(
            '$relative_Phase_unit_ocr',
            direction='left',
            offset=6,
        )
    elif phase_range == '250 ms to 450 ms':
        min_phase_value, max_phase_value = '250', '450'
        parameters.click_ocr_relative(
            '$absolute_Phase_unit_ocr',
            direction='left',
            offset=6,
        )
        absolute_phase_list = parameters.get_text(
            '$absolute_phase_list',
            first_only=False,
        )
        if min(absolute_phase_list) != min_phase_value:
            raise Exception('min_phase_value is not "250"')
        if max(absolute_phase_list) != max_phase_value:
            raise Exception('max_phase_value is not "450"')
        parameters.click_ocr_relative(
            '$absolute_Phase_unit_ocr',
            direction='left',
            offset=6,
        )
    else:
        raise Exception(
            'phase_range value not is "35% to 85%" or "250 ms to 450 ms"'
        )

@then('the phase tolerance range shown on the Display Interface is "{phase_tolerance_range}"')
def then_phase_tolerance_range(context, phase_tolerance_range):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    if phase_tolerance_range == '0% to 5%':
        min_phase_tolerance_value, max_phase_tolerance_value = '0', '5'
        parameters.click_ocr_relative(
            '$relative_Phase_tolerance_unit_ocr',
            direction='left',
            offset=6,
        )
        relative_phase_tolerance_list = parameters.get_text(
            '$relative_phase_tolerance_list',
            first_only=False,
        )
        if min(relative_phase_tolerance_list) != min_phase_tolerance_value:
            raise Exception('min_phase_tolerance_value is not "0"')
        if max(relative_phase_tolerance_list) != max_phase_tolerance_value:
            raise Exception('max_phase_tolerance_value is not "5"')
        parameters.click_ocr_relative(
            '$relative_Phase_tolerance_unit_ocr',
            direction='left',
            offset=6,
        )
    elif phase_tolerance_range == '0 ms to 100 ms':
        min_phase_tolerance_value, max_phase_tolerance_value = '0', '100'
        parameters.click_ocr_relative(
            '$absolute_Phase_tolerance_unit_ocr',
            direction='left',
            offset=6,
        )
        absolute_phase_tolerance_list = parameters.get_text(
            '$absolute_phase_tolerance_list',
            first_only=False,
        )
        if min(absolute_phase_tolerance_list) != min_phase_tolerance_value:
            raise Exception('min_phase_tolerance_value is not "0"')
        if max(absolute_phase_tolerance_list) != max_phase_tolerance_value:
            raise Exception('max_phase_tolerance_value is not "100"')
        parameters.click_ocr_relative(
            '$absolute_Phase_tolerance_unit_ocr',
            direction='left',
            offset=6,
        )
    else:
        raise Exception(
            'phase_tolerance_range value not is "0% to 5%" '
            'or "0 ms to 100 ms"'
        )
# Scenario Outline: Parameter ranges and initial values follow the selected cardiac phase mode ------------



#   Scenario Outline: Phase tolerance value follows the selected Phase value -------------------
@given('the cardiac phase mode is set to "Absolute" on the Display Interface')
def when_display_interface_displays_cardiac_phase_mode(context):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    parameters.click('$scroll_bar')
    parameters.scroll_to(target='$scroll_bar')
    parameters.click('$absolute_button')

@when('the Phase value is set to "{phase_value}" on the Display Interface')
def when_phase_value_is_set(context, phase_value):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_value = re.sub(r"\D", "", phase_value)
    parameters.input_text('$relative_Phase_edit_box', phase_value)

@then('the phase tolerance value shown on the Display Interface is "{phase_tolerance_value}"')
def then_phase_tolerance_value(context, phase_tolerance_value):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_tolerance_value = re.sub(r"\D", "", phase_tolerance_value)
    parameters.click_ocr_relative(
        '$absolute_Phase_tolerance_unit_ocr',
        direction='left',
        offset=6,
    )
    absolute_phase_tolerance_list = parameters.get_text(
        '$absolute_phase_tolerance_list',
        first_only=False,
    )
    if max(absolute_phase_tolerance_list) != phase_tolerance_value:
        raise Exception('phase_tolerance_value is not expected')
#   Scenario Outline: Phase tolerance value follows the selected Phase value -------------------


#   Scenario Outline: Absolute delay and phase tolerance values are constrained by supported boundaries and resolutions -----

# given the cardiac phase mode is set to "Absolute" on the Display Interface

@when('the phase and phase tolerance configuration limits are displayed on the Display Interface')
def when_phase_and_phase_tolerance_configuration_limits_are_displayed(context):
    pass

@when('the phase is set to "{phase_input}" on the Display Interface')
def when_patient_is_registered(context, phase_input):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    if phase_input.endswith('%'):
        phase_input = re.sub(r"\D", "", phase_input)
        parameters.input_text('$relative_Phase_edit_box', phase_input)
        parameters.click('$relative_Phase_unit_ocr')
    else:
        phase_input = re.sub(r"\D", "", phase_input)
        parameters.input_text('$absolute_Phase_edit_box', phase_input)
        parameters.click('$absolute_Phase_unit_ocr')


@then('the phase shown on the Display Interface is "{expected_phase}"')
def then_phase_shown(context, expected_phase):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    expected_phase = re.sub(r"\D", "", expected_phase)
    parameters.assert_text_equal('$absolute_Phase_edit_box', expected_phase)

@when('the phase tolerance is set to "{phase_tolerance_input}" on the Display Interface')
def when_phase_tolerance_is_set(context, phase_tolerance_input):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_tolerance_input = re.sub(r"\D", "", phase_tolerance_input)
    parameters.input_text('$absolute_Phase_edit_box', 350)
    parameters.input_text(
        '$absolute_Phase_tolerance_edit_box',
        phase_tolerance_input,
    )
    parameters.click('$absolute_Phase_unit_ocr')

@then('the phase tolerance shown on the Display Interface is "{expected_phase_tolerance}"')
def then_phase_tolerance_shown(context, expected_phase_tolerance):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    expected_phase_tolerance = re.sub(
        r"\D",
        "",
        expected_phase_tolerance,
    )
    parameters.assert_text_equal(
        '$absolute_Phase_tolerance_edit_box',
        expected_phase_tolerance,
    )
#   Scenario Outline: Absolute delay and phase tolerance values are constrained by supported boundaries and resolutions -----












