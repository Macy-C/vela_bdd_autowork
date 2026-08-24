from pathlib import Path
from time import sleep

from behave import given, then, when
from Bdd.page_obj.patient_directory.page import PatientDirectory
from Bdd.page_obj.switch_screen.page import SwitchScreenPage
from autowork_core.page import get_page
from autowork_core.runtime.application_lifecycle import (
	after_app_stop,
	before_app_start,
)


_LICENSE_KEY_PATH = Path(r"C:\pms\config\System\Licensing\key")
_AD_AND_ABS_KEY = "ad_and_abs_key"
_NOT_AD_AND_ABS_KEY = "not_ad_and_abs_key"


class PendingAutomationError(RuntimeError):
	"""Marks an explicit integration point that still needs product wiring."""


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


@when("the licensing interface is opened in Preferences")
def when_licensing_interface_is_opened(context):
	pat_directory = get_page(context, PatientDirectory)
	switch_screen = get_page(context, SwitchScreenPage)

	switch_screen.toggle_screen()
	pat_directory.open_preferences_window()
	pat_directory.preferences.scroll_the_title_bar()
	sleep(1)
	pat_directory.preferences.open_licensing()
	pat_directory.preferences.scroll_the_license_list()


@then("the value of the Absolute Delay item should be empty")
def then_absolute_delay_license_value_is_empty(context):
	pat_directory = get_page(context, PatientDirectory)
	pat_directory.preferences.Absolute_Delay_license_type_is_None()


@then('the value of the Absolute Delay item should be "{expected}"')
def then_absolute_delay_license_value_equals(context, expected):
	pat_directory = get_page(context, PatientDirectory)
	pat_directory.preferences.Absolute_Delay_license_type_is_Permanent()
