import re

from behave import *
from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.plan.page import PlanPage
from autowork_core.page import get_page


# Scenario Outline: Reconstruction phase presentation follows the selected cardiac phase mode ------------
@given('a patient is registered on the Console')
def given_patient_is_registered(context):
    patient = get_page(context, PatientPage)
    patient.register_patient_for_step_and_shoot()


@given('the "Step & Shoot" protocol is selected')
def given_select_step_and_shoot(context):
    plan = get_page(context, PlanPage)
    plan.select_step_and_shoot_ax()


@given('the clinical sequence parameters are open on the Display Interface')
def given_clinical_sequence_parameters_are_open(context):
    plan = get_page(context, PlanPage)
    plan.open_all_parameters()


@given('the cardiac phase mode is set to "{cardiac_phase_mode}" on the Display Interface')
def given_cardiac_phase_mode(context, cardiac_phase_mode):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    parameters.click('$scroll_bar')
    parameters.scroll_to(target='$scroll_bar')
    if cardiac_phase_mode in ('relative', 'Relative'):
        parameters.click('$relative_button')
    else:
        parameters.click('$absolute_button')


@given('the reconstruction phase is set to "{reconstruction_phase}" on the Display Interface')
def given_reconstruction_phase_is_set(context, reconstruction_phase):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_value = re.sub(r"\D", "", reconstruction_phase)
    if reconstruction_phase.endswith('%'):
        parameters.input_text('$relative_Phase_edit_box', phase_value)
        parameters.click('$relative_Phase_unit_ocr')
    else:
        parameters.input_text('$absolute_Phase_edit_box', phase_value)
        parameters.click('$absolute_Phase_unit_ocr')


@given('the phase tolerance is set to "{phase_tolerance}" on the Display Interface')
def given_phase_tolerance_is_set(context, phase_tolerance):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    phase_tolerance_value = re.sub(r"\D", "", phase_tolerance)
    if phase_tolerance.endswith('%'):
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


@when('the reconstruction sequence is selected')
def when_reconstruction_sequence_is_selected(context):
    plan = get_page(context, PlanPage)
    plan.click('$step_and_shoot_4_1')


@then('the reconstruction phase range shown on the Display Interface is "{reconstruction_phase_range}"')
def then_reconstruction_phase_range_shown(context, reconstruction_phase_range):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    if reconstruction_phase_range == '73 to 83':
        min_phase_value, max_phase_value = '73', '83'
        parameters.expand_dropdown('$ecg_relative_phase_ComboBox')
        relative_phase_list = parameters.get_text(
            '$ecg_relative_phase_list',
            first_only=False,
        )
        if 'Precise Phase' in relative_phase_list:
            relative_phase_list.remove('Precise Phase')
        if min(relative_phase_list) != min_phase_value:
            raise Exception('min_phase_value is not "73"')
        if max(relative_phase_list) != max_phase_value:
            raise Exception('max_phase_value is not "83"')
    elif reconstruction_phase_range == '250 to 450':
        min_phase_value, max_phase_value = '250', '450'
        parameters.expand_dropdown('$ecg_absolute_phase_ComboBox')
        absolute_phase_list = parameters.get_text(
            '$ecg_absolute_phase_list',
            first_only=False,
        )
        if 'Precise Phase' in absolute_phase_list:
            absolute_phase_list.remove('Precise Phase')
        if min(absolute_phase_list) != min_phase_value:
            raise Exception('min_phase_value is not "73"')
        if max(absolute_phase_list) != max_phase_value:
            raise Exception('max_phase_value is not "83"')
    elif reconstruction_phase_range == '78':
        parameters.assert_attr_equal(
            '$ecg_relative_phase_ComboBox',
            'Value.Value',
            reconstruction_phase_range,
        )
    else:
        parameters.assert_attr_equal(
            '$ecg_absolute_phase_ComboBox',
            'Value.Value',
            reconstruction_phase_range,
        )


@then('the reconstruction phase unit shown on the Display Interface is "{reconstruction_phase_unit}"')
def then_reconstruction_phase_unit_shown(context, reconstruction_phase_unit):
    plan = get_page(context, PlanPage)
    parameters = plan.all_parameters
    if reconstruction_phase_unit == '%':
        parameters.assert_text_equal(
            '$ecg_relative_phase_unit',
            reconstruction_phase_unit,
        )
    else:
        parameters.assert_text_equal(
            '$ecg_absolute_phase_unit',
            reconstruction_phase_unit,
        )

@then('the reconstructed series name includes "{series_name}"')
def then_reconstructed_series_name_includes(context, series_name):
    plan = get_page(context, PlanPage)
    expect1, expect2, expect3, expect4 = series_name.split(',')
    plan.assert_text_contains('$step_and_shoot_4_1_series_name', expect1)
    plan.assert_text_contains('$step_and_shoot_4_1_series_name', expect2)
    plan.assert_text_contains('$step_and_shoot_4_1_series_name', expect3)
    plan.assert_text_contains('$step_and_shoot_4_1_series_name', expect4)
# Scenario Outline: Reconstruction phase presentation follows the selected cardiac phase mode ------------