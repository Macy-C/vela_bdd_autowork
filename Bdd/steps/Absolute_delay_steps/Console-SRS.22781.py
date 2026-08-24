from pathlib import Path
from time import sleep

from behave import given, then, when

from Bdd.page_obj.patient.page import PatientPage
from Bdd.page_obj.patient_directory.page import PatientDirectory
from Bdd.page_obj.plan.page import PlanPage
from Bdd.page_obj.scanner_workflow import ScannerWorkflowPage
from Bdd.page_obj.simulator.page import SimulatorPage
from Bdd.page_obj.switch_screen.page import SwitchScreenPage
from Bdd.page_obj.view2.view2 import View2
from Bdd.page_obj.warning.page import WarningPage
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


@given("a patient is registered with the Coronary CTA protocol")
def given_patient_is_registered_with_coronary_cta(context):
	patient = get_page(context, PatientPage)
	patient.register_patient_for_coronary_cta()


@given("the scan and online reconstruction are performed")
def given_scan_and_online_reconstruction_are_performed(context):
	plan = get_page(context, PlanPage)
	simulator = get_page(context, SimulatorPage)

	plan.right_click('$Locator_locator_2')
	plan.click('$Locator_locator_2_delete')

	simulator.bring_to_front('$Simulator_window', activate=True)
	if simulator.ensure_ecg_on():
		if plan.wait_visible('$MessageBox_window', timeout=8):
			plan.click('$MessageBox_OK_button')

	simulator.minimize_window('$Simulator_window')
	plan.click('$go_scan_button')
	plan.wait_enabled('$Cancel_scan_button')

	simulator.bring_to_front('$Simulator_window', activate=True)
	simulator.wait_ready('$Simulator_window')
	sleep(2)
	simulator.start_auto_scan()
	sleep(20)

	simulator.minimize_window('$Simulator_window')
	plan.wait_enabled('$go_scan_button', timeout=20)
	plan.click('$go_scan_button')
	plan.wait_enabled('$Cancel_scan_button')

	simulator.bring_to_front('$Simulator_window', activate=True)
	sleep(3)
	simulator.start_auto_scan()
	sleep(20)
	simulator.minimize_window('$Simulator_window')

	plan.acquisition.click('$start_final_recon_button')
	scanwf = get_page(context, ScannerWorkflowPage)
	scanwf.wait_enabled('$view_button',timeout=20)

	sleep(2)
	scanwf.click('$endExam_button')
	sleep(9)

	warning = get_page(context, WarningPage)
	if warning.wait_until_open():
		warning.click('$warning_ok_button')

	switch_screen = get_page(context, SwitchScreenPage)
	switch_screen.toggle_screen()

@when("offline reconstruction is performed based on the current results")
def when_offline_reconstruction_is_performed(context):
	patientD = get_page(context, PatientDirectory)
	patientD.input_text('$Patient_ID_input',patientD.get_variable('patient_id'))
	# patientD.input_text('$Patient_ID_input','00000026')
	patientD.click('$studies_first_result')

	patientD.input_text('$Series_No_input','201')
	patientD.click('$Series_first_result')
	patientD.click('$recon_button')
	sleep(5)

	view2 = get_page(context, View2)
	view2.click('$view2_show_all_button')


@then(
	"the absolute-delay-based cardiac reconstruction option can be selected"
)
def then_absolute_delay_cardiac_reconstruction_can_be_selected(context):
	view2 = get_page(context, View2)
	view2.assert_visible('$absolute_option')
