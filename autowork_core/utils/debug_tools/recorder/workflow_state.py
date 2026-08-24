from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from autowork_core.utils.debug_tools.recorder.writer import write_json_atomic


WORKFLOW_STATE_VERSION = "3.0"
WORKFLOW_STATUSES = {
    "draft",
    "ready",
    "needs_adjustment",
    "forensic",
    "blocked",
    "stale",
    "running",
    "completed",
    "failed",
}
def load_workflow_state(session_dir, request_id):
    if not request_id:
        return {}
    path = _state_path(session_dir, request_id)
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def write_workflow_state(session_dir, state):
    _assert_state(state)
    path = _state_path(session_dir, state["request_id"])
    write_json_atomic(path, state)
    return path


def transition_workflow(
        session_dir,
        request_id,
        *,
        status,
        transaction=None,
        result=None,
):
    if status not in WORKFLOW_STATUSES:
        raise ValueError(f"无效 workflow status: {status}")
    state = load_workflow_state(session_dir, request_id)
    if not state:
        raise FileNotFoundError(f"workflow state 不存在: {request_id}")
    state["status"] = status
    state["next_action"] = next_workflow_action(status)
    state["updated_at"] = datetime.now().isoformat(timespec="seconds")
    state["active_transaction"] = transaction
    if result is not None:
        state["last_result"] = result
    write_workflow_state(session_dir, state)
    return state


def workflow_status_for_request(session_dir, request):
    state = load_workflow_state(session_dir, request.get("request_id"))
    if not state:
        return "draft"
    expected = (request.get("revision_snapshot") or {}).get("seal")
    actual = (state.get("revision") or {}).get("seal")
    if not state or not expected or expected != actual:
        return "stale"
    return state.get("status") or "draft"


def next_workflow_action(status):
    return {
        "draft": "inspect",
        "ready": "generate",
        "needs_adjustment": "answer_decision_pack",
        "forensic": "inspect_named_evidence_and_submit_plan",
        "blocked": "repair_or_minimally_rerecord",
        "stale": "materialize_latest_request",
        "running": "finish_generation_transaction",
        "completed": "review_or_regenerate",
        "failed": "repair_generation_output",
    }[status]


def _assert_state(state):
    status = state.get("status")
    if status not in WORKFLOW_STATUSES:
        raise ValueError(f"workflow state 无效: {status}")
    if not state.get("request_id"):
        raise ValueError("workflow state 缺少 request_id")


def _state_path(session_dir, request_id):
    return Path(session_dir).resolve() / "ai" / "workflow" / f"{request_id}.json"


