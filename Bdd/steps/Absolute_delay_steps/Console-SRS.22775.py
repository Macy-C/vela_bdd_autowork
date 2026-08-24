from behave import given, then

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
	parameters.scroll_to(target='$scroll_bar')

@then(
	"the corresponding supported value should be displayed for each "
	"entered absolute phase value:"
)
def then_supported_absolute_phase_values_are_displayed(context):
	rows = [row.as_dict() for row in context.table]
	plan = get_page(context, PlanPage)
	parameters = plan.all_parameters

	for row in rows:
		entered_phase = row['entered_phase']
		displayed_phase = row['displayed_phase']

		parameters.input_text('$absolute_Phase_edit_box', entered_phase)
		parameters.click('$absolute_Phase_unit_ocr')

		parameters.assert_attr_equal('$absolute_Phase_edit_box','Value.Value',displayed_phase)
