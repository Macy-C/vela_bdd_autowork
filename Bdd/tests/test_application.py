import unittest
from unittest.mock import call, patch

from Bdd import application


class ApplicationTests(unittest.TestCase):
    def test_start_application_hides_background_processes_without_waiting(self):
        with (
            patch.object(application, "_run_command") as run_command,
            patch.object(application, "_start_file") as start_file,
            patch.object(application, "_start_hidden_file") as start_hidden,
            patch.object(application, "sleep") as sleep,
        ):
            application.start_application()

        self.assertEqual(
            [
                call(["net.exe", "start", service])
                for service in application.BASE_SERVICES
            ],
            run_command.call_args_list,
        )
        self.assertEqual(
            [
                *(call(app) for app in application.GANTRY_APPS),
                call(application.PMS_WINDOWS_PRINTING),
                call(application.PRODUCT_LOGON),
            ],
            start_hidden.call_args_list,
        )
        start_file.assert_not_called()
        sleep.assert_called_once_with(5)

    def test_start_simulator_hides_background_processes_but_shows_client(self):
        with (
            patch.object(application, "_run_command") as run_command,
            patch.object(application, "_start_file") as start_file,
            patch.object(
                application,
                "_start_hidden_file",
            ) as start_hidden,
            patch.object(application, "sleep") as sleep,
        ):
            application.start_simulator()

        self.assertEqual(
            [
                *(call(["net.exe", "start", service])
                  for service in application.BASE_SERVICES),
                *(call(["net.exe", "start", service])
                  for service in application.GANTRY_SERVICES),
            ],
            run_command.call_args_list,
        )
        self.assertEqual(
            [
                *(call(app) for app in application.GANTRY_APPS),
                call(application.SIMULATOR_ENGINE),
            ],
            start_hidden.call_args_list,
        )
        start_file.assert_called_once_with(application.SIMULATORS)
        self.assertEqual(
            [call(5), call(5)],
            sleep.call_args_list,
        )

    def test_stop_application_launches_gantry_registration_without_waiting(self):
        events = []

        def run_command(command):
            events.append(("run", command))

        def start_file(file_path):
            events.append(("start", file_path))

        def start_hidden_file(file_path, *arguments):
            events.append(("start-hidden", file_path, arguments))

        with (
            patch.object(
                application,
                "_run_command",
                side_effect=run_command,
            ),
            patch.object(
                application,
                "_start_file",
                side_effect=start_file,
            ),
            patch.object(
                application,
                "_start_hidden_file",
                side_effect=start_hidden_file,
            ),
            patch.object(
                application,
                "sleep",
                side_effect=lambda seconds: events.append(("sleep", seconds)),
            ),
        ):
            application.stop_application()

        self.assertEqual(
            [
                *(
                    ("run", ["taskkill.exe", "/im", name, "/f", "/t"])
                    for name in application.PROCESS_NAMES
                ),
                ("sleep", 5),
                (
                    "start-hidden",
                    application.REGISTER_GANTRY_SERVERS,
                    ("/a",),
                ),
                *(
                    ("run", ["net.exe", "start", name])
                    for name in application.POST_STOP_SERVICES
                ),
                (
                    "start-hidden",
                    application.GANTRY_SERVICE_HOST,
                    (),
                ),
            ],
            events,
        )

    def test_start_hidden_file_uses_hidden_shell_execute_for_executable(self):
        with (
            patch.object(application.os, "startfile") as startfile,
            patch.object(application.subprocess, "Popen") as popen,
        ):
            result = application._start_hidden_file(
                application.SIMULATOR_ENGINE,
            )

        startfile.assert_called_once_with(
            application.SIMULATOR_ENGINE,
            cwd=str(
                application.Path(application.SIMULATOR_ENGINE).parent
            ),
            show_cmd=application.subprocess.SW_HIDE,
        )
        popen.assert_not_called()
        self.assertIsNone(result)

    def test_run_command_hides_window_without_changing_execution_contract(self):
        working_directory = r"C:\Pms\bin"
        startupinfo = object()
        with (
            patch.object(application.subprocess, "run") as run,
            patch.object(
                application,
                "_hidden_startupinfo",
                return_value=startupinfo,
            ),
        ):
            completed = application._run_command(
                ["net.exe", "start", "Example Service"],
                cwd=working_directory,
            )

        run.assert_called_once_with(
            ["net.exe", "start", "Example Service"],
            cwd=working_directory,
            capture_output=True,
            text=True,
            check=False,
            startupinfo=startupinfo,
        )
        self.assertIs(run.return_value, completed)

    def test_hidden_startupinfo_only_controls_initial_window_visibility(self):
        startupinfo = application._hidden_startupinfo()

        self.assertTrue(
            startupinfo.dwFlags & application.subprocess.STARTF_USESHOWWINDOW
        )
        self.assertEqual(application.subprocess.SW_HIDE, startupinfo.wShowWindow)

    def test_start_file_uses_visible_shell_execute_and_parent_directory(self):
        with patch.object(application.os, "startfile") as startfile:
            result = application._start_file(application.SIMULATORS)

        startfile.assert_called_once_with(
            application.SIMULATORS,
            cwd=str(application.Path(application.SIMULATORS).parent),
            show_cmd=1,
        )
        self.assertIsNone(result)

    def test_start_hidden_file_wraps_batch_with_hidden_cmd(self):
        startupinfo = object()
        with (
            patch.object(application.subprocess, "Popen") as popen,
            patch.object(
                application,
                "_hidden_startupinfo",
                return_value=startupinfo,
            ),
        ):
            process = application._start_hidden_file(
                application.REGISTER_GANTRY_SERVERS,
                "/a",
            )

        popen.assert_called_once_with(
            [
                "cmd.exe",
                "/d",
                "/c",
                application.REGISTER_GANTRY_SERVERS,
                "/a",
            ],
            cwd=str(
                application.Path(application.REGISTER_GANTRY_SERVERS).parent
            ),
            stdin=application.subprocess.DEVNULL,
            stdout=application.subprocess.DEVNULL,
            stderr=application.subprocess.DEVNULL,
            startupinfo=startupinfo,
            close_fds=True,
        )
        self.assertIs(popen.return_value, process)

if __name__ == "__main__":
    unittest.main()