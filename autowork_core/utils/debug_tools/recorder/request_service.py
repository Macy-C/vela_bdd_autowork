from __future__ import annotations

import threading
from pathlib import Path

from autowork_core.utils.debug_tools.recorder import request_repository
from autowork_core.utils.debug_tools.recorder.generation_request import (
    build_generation_request,
)
from autowork_core.utils.debug_tools.recorder.generation_contract import (
    ensure_generation_contract,
)
from autowork_core.utils.debug_tools.recorder.project_memory import (
    inspect_request_memory_freshness,
)
from autowork_core.utils.debug_tools.recorder.workflow_service import (
    inspect_workflow,
)
from autowork_core.utils.debug_tools.recorder.workflow_state import (
    load_workflow_state,
)


_SESSION_LOCKS = {}
_SESSION_LOCKS_GUARD = threading.Lock()


class GenerationRequestService:
    def __init__(self, session_dir):
        self.session_dir = Path(session_dir).resolve()
        self._lock = _session_lock(self.session_dir)

    def latest(self, step_ids):
        with self._lock:
            step_ids = request_repository.normalize_step_ids(step_ids)
            request = request_repository.find_latest_request(
                self.session_dir,
                step_ids,
            )
            if not request_repository.request_identity_is_valid(
                request,
                step_ids,
            ):
                return None
            state = load_workflow_state(
                self.session_dir,
                request.get("request_id"),
            )
            if state.get("status") == "running":
                return request
            if not request_repository.request_matches_current_evidence(
                self.session_dir,
                request,
                step_ids,
            ):
                return None
            freshness = inspect_request_memory_freshness(
                self.session_dir,
                request,
            )
            if freshness["status"] in {"compatible", "matched"}:
                return request
            return None

    def ensure_latest(self, step_ids, *, repair=False):
        with self._lock:
            ensure_generation_contract(self.session_dir, write=True)
            step_ids = request_repository.normalize_step_ids(step_ids)
            request = self.latest(step_ids)
            if request is not None and not repair:
                return request
            return build_generation_request(
                self.session_dir,
                steps=list(step_ids),
                write=True,
                repair=repair,
            )

    def generation_command(self, step_ids):
        request = self.latest(step_ids)
        if request is None:
            request = self.ensure_latest(step_ids, repair=True)
        path = request_repository.resolve_request_path(
            self.session_dir,
            request["request_path"],
        )
        return f'/recorder-generate "{path}"'

    def workflow_state(self, step_ids, *, refresh=False):
        request = self.latest(step_ids)
        if request is None:
            return {}
        if not refresh:
            state = load_workflow_state(
                self.session_dir,
                request.get("request_id"),
            )
            if state:
                return state
        path = request_repository.resolve_request_path(
            self.session_dir,
            request["request_path"],
        )
        return inspect_workflow(path, write=True)


def _session_lock(session_dir):
    key = str(Path(session_dir).resolve()).casefold()
    with _SESSION_LOCKS_GUARD:
        return _SESSION_LOCKS.setdefault(key, threading.RLock())