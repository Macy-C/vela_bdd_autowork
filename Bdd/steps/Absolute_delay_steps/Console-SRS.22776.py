from behave import given, then, when

from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.plan.page import PlanPage
from autowork_core.page import get_page


class PendingAutomationError(RuntimeError):
	"""Marks a Step that still needs Recorder generation."""


@given("a patient is registered on the console")
def given_patient_is_registered(context):
	patient = get_page(context, PatientPage)
	patient.register_patient_for_step_and_shoot()


@given('the "Step & Shoot" protocol is selected')
def given_step_and_shoot_protocol_is_selected(context):
	pass


@given("the clinical sequence parameters are open on the Display Interface")
def given_clinical_sequence_parameters_are_open(context):
	plan = get_page(context, PlanPage)
	plan.select_step_and_shoot_ax()
	plan.open_all_parameters()


@given(
	'the cardiac phase mode is set to "Absolute" '
	"on the Display Interface"
)
def given_cardiac_phase_mode_is_absolute(context):
	plan = get_page(context, PlanPage)
	parameters = plan.all_parameters
	parameters.click('$All_parameters_tag')
	parameters.click('$absolute_button')
	parameters.click('$scroll_bar')
	parameters.scroll_to(target='$scroll_bar',steps=10)


@when("the phase value is set to 350")
def when_phase_value_is_set_to_350(context):
	plan = get_page(context, PlanPage)
	parameters = plan.all_parameters
	parameters.input_text('$absolute_Phase_edit_box', 350)
	parameters.click('$absolute_Phase_unit_ocr')


@then(
	"the corresponding supported value should be displayed for each "
	"entered phase tolerance value:"
)
def then_supported_phase_tolerance_values_are_displayed(context):
	rows = [row.as_dict() for row in context.table]
	plan = get_page(context, PlanPage)
	parameters = plan.all_parameters

	for row in rows:
		phase_tolerance_input = row['phase_tolerance_input']
		expected_phase_tolerance = row['expected_phase_tolerance']
		parameters.input_text('$absolute_Phase_tolerance_edit_box',phase_tolerance_input)
		parameters.click('$absolute_Phase_unit_ocr')
		parameters.assert_attr_equal('$absolute_Phase_tolerance_edit_box','Value.Value',expected_phase_tolerance)


@then(
	"the corresponding phase tolerance value should be displayed for each "
	"entered phase and phase tolerance combination:"
)
def then_phase_tolerance_combinations_are_displayed(context):
	rows = [row.as_dict() for row in context.table]
	plan = get_page(context, PlanPage)
	parameters = plan.all_parameters

	for row in rows:
		phase_value = row['phase_value']
		phase_tolerance_input = row['phase_tolerance_input']
		expected_phase_tolerance = row['expected_phase_tolerance']

		parameters.input_text('$absolute_Phase_edit_box', phase_value)
		parameters.click('$absolute_Phase_unit_ocr')
		parameters.input_text('$absolute_Phase_tolerance_edit_box',phase_tolerance_input)
		parameters.click('$absolute_Phase_unit_ocr')

		parameters.assert_attr_equal('$absolute_Phase_tolerance_edit_box','Value.Value',expected_phase_tolerance)


@then("the prompt range should be independently displayed for each entered phase and phase tolerance combination:")
def then_prompt_ranges_are_displayed(context):
	rows = [row.as_dict() for row in context.table]
	plan = get_page(context, PlanPage)
	parameters = plan.all_parameters

	for row in rows:
		phase_value = row['phase_value']
		phase_tolerance_input = row['phase_tolerance_input']
		expected_range = row['expected_range']

		parameters.input_text('$absolute_Phase_edit_box', phase_value)
		parameters.click('$absolute_Phase_unit_ocr')
		parameters.input_text('$absolute_Phase_tolerance_edit_box',phase_tolerance_input)
		parameters.click('$absolute_Phase_unit_ocr')

		if expected_range == '0':
			parameters.assert_not_exists('$range_prompt_msg')
		else:
			parameters.assert_attr_contains('$range_prompt_msg','name',expected_range)
