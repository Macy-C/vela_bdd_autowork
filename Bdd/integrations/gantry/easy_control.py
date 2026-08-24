"""Python wrapper around the managed ``GantryEasyControl.dll`` (.NET Framework 4.7.2).

Interop is done with `pythonnet <https://github.com/pythonnet/pythonnet>`_ (the ``clr``
module), which hosts the CLR in-process and exposes the .NET types directly.

The wrapper surfaces the *complete* public API of the assembly:

* :class:`GantryEasyControl` — facade over ``EasyControl`` (implements the
  ``IEasyControl`` and ``IGeminiGantryDemo`` interfaces). All methods, the
  ``CouchSpeed`` property and every event are exposed.
* :class:`CouchControl` — facade over the standalone ``CouchControl`` class.
* Enums (``GantryStates``, ``ErrorLevels``, ``DoorStates``, ``ReturnStatus``) are
  attached to each facade instance for convenient argument/return comparisons.

Quick start
-----------
::

    from Bdd.integrations.gantry import GantryEasyControl

    with GantryEasyControl() as gantry:
        gantry.close_gantry_estop()
        gantry.move_couch_vertical_to_position(move_up=True, vertical_position=100, relative=False)

        # Events: subscribe with a plain Python callable.
        def on_state(state):
            print("gantry state:", state)
        gantry.on_gantry_state_changed(on_state)
        # ... later ...
        gantry.unsubscribe("gantry_state_changed", on_state)

Important notes
---------------
* The runtime is forced to ``netfx`` (the .NET Framework CLR) *before* ``clr`` is
  imported, because the DLL targets net472.
* ``GantryEasyControl.dll`` depends on ``CanmsTypes.dll`` (and possibly further
  assemblies). Every dependency must live in ``dll_dir``; an ``AssemblyResolve``
  handler loads them on demand. Until ``CanmsTypes.dll`` is present, constructing
  the facades will fail with an assembly-load error.
* Every ``IEasyControl`` / ``IGeminiGantryDemo`` member (methods *and* events) is an
  *explicit* interface implementation on ``EasyControl``, so it is only reachable by
  casting the instance to the interface. The facade does this for you.
* Match the Python interpreter bitness to the DLLs. If ``CanmsTypes`` (CAN messaging)
  pulls in x86 native code, run 32-bit Python; otherwise 64-bit is fine.
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from types import SimpleNamespace
from typing import Callable

_ASSEMBLY_LOCK = threading.Lock()
_LOADED: "dict[str, SimpleNamespace]" = {}
DEFAULT_DLL_DIR = (
    Path(__file__).resolve().parent
    / "bin"
)


def _ensure_netfx_runtime() -> None:
    """Select the .NET Framework CLR. Must run before ``import clr``."""
    os.environ.setdefault("PYTHONNET_RUNTIME", "netfx")
    try:
        from pythonnet import set_runtime  # pythonnet >= 3.0
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise ImportError(
            "pythonnet is required for the gantry wrapper. Install it with "
            "'pip install pythonnet'."
        ) from exc

    if "clr" not in sys.modules:
        # No-op if the CLR is already started; guarded so re-import is safe.
        set_runtime("netfx")


def _load(dll_dir: str, assembly_name: str = "GantryEasyControl") -> SimpleNamespace:
    """Load the assembly (once per directory) and return its resolved .NET types.

    :param dll_dir: Folder containing ``GantryEasyControl.dll`` and its
        dependencies (e.g. ``CanmsTypes.dll``).
    :param assembly_name: Assembly simple name (no extension).
    :returns: A namespace with the classes and enums used by the facades.
    """
    dll_dir = os.path.abspath(dll_dir)
    with _ASSEMBLY_LOCK:
        cached = _LOADED.get(dll_dir)
        if cached is not None:
            return cached

        if not os.path.isdir(dll_dir):
            raise FileNotFoundError(f"DLL directory not found: {dll_dir}")

        _ensure_netfx_runtime()

        import clr  # noqa: E402  (import after runtime selection)
        from System import AppDomain, ResolveEventHandler
        from System.Reflection import Assembly

        # Resolve dependent assemblies (CanmsTypes, ...) from the same folder.
        def _resolve(_sender, args):
            simple_name = args.Name.split(",")[0].strip()
            candidate = os.path.join(dll_dir, simple_name + ".dll")
            return Assembly.LoadFrom(candidate) if os.path.isfile(candidate) else None

        resolver = ResolveEventHandler(_resolve)
        AppDomain.CurrentDomain.AssemblyResolve += resolver

        if dll_dir not in sys.path:
            sys.path.append(dll_dir)
        clr.AddReference(os.path.join(dll_dir, assembly_name + ".dll"))

        import GantryEasyControl as _g  # the .NET namespace

        types = SimpleNamespace(
            EasyControl=_g.EasyControl,
            IEasyControl=_g.IEasyControl,
            IGeminiGantryDemo=_g.IGeminiGantryDemo,
            CouchControl=getattr(_g, "CouchControl", None),
            GantryStates=_g.GantryStates,
            ErrorLevels=_g.ErrorLevels,
            DoorStates=_g.DoorStates,
            ReturnStatus=getattr(_g, "ReturnStatus", None),
            _resolver=resolver,
        )
        _LOADED[dll_dir] = types
        return types


class GantryEasyControl:
    """Facade over ``GantryEasyControl.EasyControl``.

    Exposes the union of the ``IEasyControl`` and ``IGeminiGantryDemo`` interfaces.
    All calls are routed through the appropriate explicit-interface view.
    """

    # friendly event name -> (interface attribute, .NET event name)
    _EVENTS = {
        "couch_position_changed": ("_ie", "CouchPositionChanged"),
        "gantry_state_changed": ("_ie", "GantryStateChanged"),
        "gantry_error_occurred": ("_ie", "GantryErrorOccurred"),
        "gantry_xray_status_changed": ("_ie", "GantryXRayStatusChanged"),
        "gantry_door_status_changed": ("_ie", "GantryDoorStatusChanged"),
        "gantry_config_end_bkst": ("_ig", "GantryConfigEndBkst"),
        "rhost_estop_closed_req": ("_ig", "RhostEstopClosedReq"),
        "dmc_estop_closed_req": ("_ig", "DmcEstopClosedReq"),
        "gantry_pet_homed_bkst": ("_ig", "GantryPetHomedBkst"),
    }

    def __init__(self, dll_dir=None, assembly_name: str = "GantryEasyControl"):
        dll_dir = str(dll_dir or DEFAULT_DLL_DIR)
        self._types = _load(dll_dir, assembly_name)
        self._easy = self._types.EasyControl()
        # Explicit-interface views: every member lives on one of these.
        self._ie = self._types.IEasyControl(self._easy)
        self._ig = self._types.IGeminiGantryDemo(self._easy)

        # Enums exposed for convenient comparisons in caller code.
        self.GantryStates = self._types.GantryStates
        self.ErrorLevels = self._types.ErrorLevels
        self.DoorStates = self._types.DoorStates
        self.ReturnStatus = self._types.ReturnStatus
        self._subscriptions = []
        self._closed = False

    # -- raw / interface access ---------------------------------------------

    @property
    def raw(self):
        """The underlying .NET ``EasyControl`` instance."""
        return self._easy

    @property
    def easy_control(self):
        """The instance cast to ``IEasyControl``."""
        return self._ie

    @property
    def gemini(self):
        """The instance cast to ``IGeminiGantryDemo``."""
        return self._ig

    # -- IEasyControl: methods ----------------------------------------------

    def close_gantry_estop(self) -> None:
        """Close the gantry emergency stop (``IEasyControl.CloseGantryEStop``)."""
        self._ie.CloseGantryEStop()

    # Backwards-compatible alias.
    close_estop = close_gantry_estop

    def enable_gantry(self) -> None:
        """``IEasyControl.EnableGantry``."""
        self._ie.EnableGantry()

    def pause_gantry(self) -> None:
        """``IEasyControl.PauseGantry``."""
        self._ie.PauseGantry()

    def auto_start_scans(self) -> None:
        """``IEasyControl.AutoStartScans``."""
        self._ie.AutoStartScans()

    def manual_start_scans(self) -> None:
        """``IEasyControl.ManualStartScans``."""
        self._ie.ManualStartScans()

    def zero_couch(self) -> None:
        """``IEasyControl.ZeroCouch``."""
        self._ie.ZeroCouch()

    def restart_gantry_rotor(self) -> None:
        """``IEasyControl.RestartGantryRotor``."""
        self._ie.RestartGantryRotor()

    def move_couch_horizontal_to_position(
        self, move_out: bool, horizontal_position: int, relative: bool
    ) -> None:
        """``IEasyControl.MoveCouchHorizontalToPosition``."""
        self._ie.MoveCouchHorizontalToPosition(move_out, horizontal_position, relative)

    def move_couch_vertical_to_position(
        self, move_up: bool, vertical_position: int, relative: bool
    ) -> None:
        """``IEasyControl.MoveCouchVerticalToPosition``."""
        self._ie.MoveCouchVerticalToPosition(move_up, vertical_position, relative)

    def get_gantry_door_switch_state(self):
        """``IEasyControl.GetGantryDoorSwitchState`` -> ``DoorStates``."""
        return self._ie.GetGantryDoorSwitchState()

    def couch_patient_unload(self) -> None:
        """``IEasyControl.CouchPatientUnload``."""
        self._ie.CouchPatientUnload()

    def move_subframe(self, *args):
        """``IEasyControl.MoveSubframe``.

        The parameter type is defined in ``CanmsTypes``; arguments are forwarded
        as-is. Pass a ``CanmsTypes`` value (e.g. obtained from the .NET side).
        """
        return self._ie.MoveSubframe(*args)

    # -- IEasyControl: property ---------------------------------------------

    @property
    def couch_speed(self) -> int:
        """``IEasyControl.CouchSpeed`` (get/set)."""
        return self._ie.CouchSpeed

    @couch_speed.setter
    def couch_speed(self, value: int) -> None:
        self._ie.CouchSpeed = value

    # -- IGeminiGantryDemo: methods -----------------------------------------

    def mark_gantry_offline(self) -> None:
        """``IGeminiGantryDemo.MarkGantryOffline``."""
        self._ig.MarkGantryOffline()

    def send_rhost_config_end_bkst(self) -> None:
        """``IGeminiGantryDemo.SendRhostConfigEndBkst``."""
        self._ig.SendRhostConfigEndBkst()

    def send_dmc_config_end_bkst(self) -> None:
        """``IGeminiGantryDemo.SendDmcConfigEndBkst``."""
        self._ig.SendDmcConfigEndBkst()

    def send_rhost_estop_closed_ans(self) -> None:
        """``IGeminiGantryDemo.SendRhostEstopClosedAns``."""
        self._ig.SendRhostEstopClosedAns()

    def send_dmc_estop_closed_ans(self) -> None:
        """``IGeminiGantryDemo.SendDmcEstopClosedAns``."""
        self._ig.SendDmcEstopClosedAns()

    def send_gantry_state_bkst_pre_series(self) -> None:
        """``IGeminiGantryDemo.SendGantryStateBkstPreSeries``."""
        self._ig.SendGantryStateBkstPreSeries()

    # -- events: generic subscribe/unsubscribe ------------------------------

    def subscribe(self, event: str, callback: Callable) -> Callable:
        """Attach a Python callable to a gantry event.

        :param event: One of :attr:`_EVENTS` (e.g. ``"gantry_state_changed"``).
        :param callback: A callable whose parameters match the event delegate.
        :returns: The callback (so it can be stored for later :meth:`unsubscribe`).

        Delegate signatures (callback parameters):

        * ``couch_position_changed(vertical_position: int, horizontal_position: int)``
        * ``gantry_state_changed(gantry_state: GantryStates)``
        * ``gantry_error_occurred(error_level: ErrorLevels, error_string: str)``
        * ``gantry_xray_status_changed(xray_on: bool)``
        * ``gantry_door_status_changed(door_state: DoorStates)``
        * ``gantry_config_end_bkst()``
        * ``rhost_estop_closed_req()``
        * ``dmc_estop_closed_req()``
        * ``gantry_pet_homed_bkst()``
        """
        target, name = self._event_target(event)
        handler = getattr(target, name)
        handler = handler.__iadd__(callback)  # equivalent to: target.<name> += callback
        setattr(target, name, handler)
        self._subscriptions.append((event, callback))
        return callback

    def unsubscribe(self, event: str, callback: Callable) -> None:
        """Detach a previously subscribed callback from a gantry event."""
        target, name = self._event_target(event)
        handler = getattr(target, name)
        handler = handler.__isub__(callback)  # equivalent to: target.<name> -= callback
        setattr(target, name, handler)
        subscription = (event, callback)
        if subscription in self._subscriptions:
            self._subscriptions.remove(subscription)

    def _event_target(self, event: str):
        try:
            attr, name = self._EVENTS[event]
        except KeyError:
            raise KeyError(
                f"Unknown event '{event}'. Known events: {sorted(self._EVENTS)}"
            ) from None
        return getattr(self, attr), name

    # -- events: named convenience helpers ----------------------------------

    def on_couch_position_changed(self, cb: Callable) -> Callable:
        return self.subscribe("couch_position_changed", cb)

    def on_gantry_state_changed(self, cb: Callable) -> Callable:
        return self.subscribe("gantry_state_changed", cb)

    def on_gantry_error_occurred(self, cb: Callable) -> Callable:
        return self.subscribe("gantry_error_occurred", cb)

    def on_gantry_xray_status_changed(self, cb: Callable) -> Callable:
        return self.subscribe("gantry_xray_status_changed", cb)

    def on_gantry_door_status_changed(self, cb: Callable) -> Callable:
        return self.subscribe("gantry_door_status_changed", cb)

    def on_gantry_config_end_bkst(self, cb: Callable) -> Callable:
        return self.subscribe("gantry_config_end_bkst", cb)

    def on_rhost_estop_closed_req(self, cb: Callable) -> Callable:
        return self.subscribe("rhost_estop_closed_req", cb)

    def on_dmc_estop_closed_req(self, cb: Callable) -> Callable:
        return self.subscribe("dmc_estop_closed_req", cb)

    def on_gantry_pet_homed_bkst(self, cb: Callable) -> Callable:
        return self.subscribe("gantry_pet_homed_bkst", cb)

    # -- lifecycle -----------------------------------------------------------

    def __enter__(self) -> "GantryEasyControl":
        return self

    def close(self) -> None:
        if self._closed:
            return

        for event, callback in reversed(self._subscriptions[:]):
            self.unsubscribe(event, callback)

        dispose = getattr(self._easy, "Dispose", None)
        if callable(dispose):
            dispose()
        self._closed = True

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
        return None


class CouchControl:
    """Facade over the standalone ``GantryEasyControl.CouchControl`` class.

    All methods return a ``ReturnStatus`` enum value (``Pass`` / ``Fail``).
    """

    def __init__(self, dll_dir=None, assembly_name: str = "GantryEasyControl"):
        dll_dir = str(dll_dir or DEFAULT_DLL_DIR)
        self._types = _load(dll_dir, assembly_name)
        if self._types.CouchControl is None:
            raise RuntimeError(
                "The loaded GantryEasyControl.dll does not expose CouchControl. "
                "Use GantryEasyControl for the API available in this DLL version."
            )
        self._couch = self._types.CouchControl()
        self.ReturnStatus = self._types.ReturnStatus

    @property
    def raw(self):
        """The underlying .NET ``CouchControl`` instance."""
        return self._couch

    # -- vertical ------------------------------------------------------------

    def vertical_jog_to_position(
        self, direction: bool, speed: int, to_position: int, move_type: bool
    ):
        """``CouchVerticalJogToPosition``."""
        return self._couch.CouchVerticalJogToPosition(direction, speed, to_position, move_type)

    def vertical_jog(self, direction: bool, speed: int):
        """``CouchVerticalJog``."""
        return self._couch.CouchVerticalJog(direction, speed)

    def continue_vertical_jog(self):
        """``CouchContinueVerticalJog``."""
        return self._couch.CouchContinueVerticalJog()

    def stop_vertical_jog(self):
        """``CouchStopVerticalJog``."""
        return self._couch.CouchStopVerticalJog()

    # -- horizontal ----------------------------------------------------------

    def horizontal_jog_to_position(
        self, direction: bool, speed: int, to_position: int, move_type: bool
    ):
        """``CouchHorizontalJogToPosition``."""
        return self._couch.CouchHorizontalJogToPosition(direction, speed, to_position, move_type)

    def horizontal_jog(self, direction: bool, speed: int):
        """``CouchHorizontalJog``."""
        return self._couch.CouchHorizontalJog(direction, speed)

    def two_speed_horizontal_jog(self, direction: bool):
        """``CouchTwoSpeedHorizontalJog``."""
        return self._couch.CouchTwoSpeedHorizontalJog(direction)

    def continue_horizontal_jog(self):
        """``CouchContinueHorizontalJog``."""
        return self._couch.CouchContinueHorizontalJog()

    def stop_horizontal_jog(self):
        """``CouchStopHorizontalJog``."""
        return self._couch.CouchStopHorizontalJog()

    # -- subframe ------------------------------------------------------------

    def subframe_jog_to_position(self, *args):
        """``SubFrameJogToPosition``.

        The parameter type is defined in ``CanmsTypes``; arguments are forwarded
        as-is.
        """
        return self._couch.SubFrameJogToPosition(*args)

    def continue_subframe_jog(self):
        """``CouchContinueSubFrameJog``."""
        return self._couch.CouchContinueSubFrameJog()

    def stop_subframe_jog(self):
        """``CouchStopSubFrameJog``."""
        return self._couch.CouchStopSubFrameJog()

    # -- patient unload ------------------------------------------------------

    def patient_unload(self):
        """``CouchPatientUnload``."""
        return self._couch.CouchPatientUnload()

    def continue_patient_unload(self):
        """``CouchContinuePatientUnload``."""
        return self._couch.CouchContinuePatientUnload()
