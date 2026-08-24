from pathlib import Path

from behave import given, then, when

from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.plan.page import PlanPage
from autowork_core.page import get_page
from autowork_core.runtime.application_lifecycle import (
	after_app_stop,
	before_app_start,
)


_LICENSE_KEY_PATH = Path(r"C:\pms\config\System\Licensing\key")
_AD_AND_ABS_KEY = "ad_and_abs_key"
_NOT_AD_AND_ABS_KEY = "not_ad_and_abs_key"


class PendingAutomationError(RuntimeError):
	"""Marks a Step that still needs Recorder generation."""


def _get_license_key(context, key_name):
	value = context.autowork_run.public_data.get(key_name)
	if not isinstance(value, str) or not value:
		raise ValueError(
			f"Bdd/data/public_data.yaml must define a non-empty {key_name!r}"
		)
	return value


def _write_license_key(context, key_name):
	if not _LICENSE_KEY_PATH.is_file():
		raise FileNotFoundError(
			f"License key file does not exist: {_LICENSE_KEY_PATH}"
		)
	expected = _get_license_key(context, key_name)
	_LICENSE_KEY_PATH.write_text(expected, encoding="utf-8")
	actual = _LICENSE_KEY_PATH.read_text(encoding="utf-8")
	if actual != expected:
		raise OSError(
			f"License key file verification failed: {_LICENSE_KEY_PATH}"
		)


@before_app_start(tags="license_without_absolute_delay")
def configure_license_without_absolute_delay(context, scenario):
	_write_license_key(context, _NOT_AD_AND_ABS_KEY)


@before_app_start(tags="license_with_absolute_delay")
def configure_license_with_absolute_delay(context, scenario):
	_write_license_key(context, _AD_AND_ABS_KEY)


@after_app_stop(tags="license_without_absolute_delay")
@after_app_stop(tags="license_with_absolute_delay")
def restore_license_configuration(context, scenario):
	_write_license_key(context, _AD_AND_ABS_KEY)


def _assert_license_key(context, key_name):
	expected = _get_license_key(context, key_name)
	actual = _LICENSE_KEY_PATH.read_text(encoding="utf-8")
	if actual != expected:
		raise AssertionError(
			"Unexpected Absolute Delay license key content: "
			f"expected public_data key={key_name!r}"
		)


@given(
	"a license that does not support Absolute Delay is configured "
	"on the Console"
)
def given_license_without_absolute_delay(context):
	_assert_license_key(context, _NOT_AD_AND_ABS_KEY)


@given("a license that supports Absolute Delay is configured on the Console")
def given_license_with_absolute_delay(context):
	_assert_license_key(context, _AD_AND_ABS_KEY)


@given("a patient is registered with the Step & Shoot protocol")
def given_patient_is_registered_with_step_and_shoot(context):
	patient = get_page(context, PatientPage)
	patient.register_patient_for_step_and_shoot()


@when("the Step & Shoot AX Parameters interface is opened")
def when_step_and_shoot_ax_parameters_are_opened(context):
	plan = get_page(context, PlanPage)
	plan.select_step_and_shoot_ax()
	plan.open_all_parameters()
	parameters = plan.all_parameters
	parameters.click('$All_parameters_tag')
	parameters.click('$scroll_bar')
	parameters.scroll_to(target='$scroll_bar')


@then(
	"the absolute-delay-based gated acquisition option cannot be selected"
)
def then_absolute_delay_gated_acquisition_cannot_be_selected(context):
	plan = get_page(context, PlanPage)
	parameters = plan.all_parameters
	parameters.assert_not_exists('$absolute_button')


@then("the absolute-delay-based gated acquisition option can be selected")
def then_absolute_delay_gated_acquisition_can_be_selected(context):
	plan = get_page(context, PlanPage)
	parameters = plan.all_parameters
	parameters.assert_exists('$absolute_button')
