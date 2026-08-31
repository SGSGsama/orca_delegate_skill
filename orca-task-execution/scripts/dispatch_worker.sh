#!/usr/bin/env bash
set -euo pipefail

# Start one fresh supervised worker from the ownership/domain/role route
# persisted on the Task. Model and effort are derived here, never supplied by
# the coordinator.

usage() {
  cat <<'EOF'
Usage:
  dispatch_worker.sh --task <task_id> --worktree <selector> [worker-start placement options]
  dispatch_worker.sh --self-test

Required:
  --task <id>                 Existing Orca orchestration Task
  --worktree <selector>       current, exact existing selector, new-child, or new-top-level

Forwarded when present:
  --run --on --name --repo --base-branch --display-name --comment --setup
  --retry-of --timeout-ms --from --retry-request

The Task spec must start with exactly:
  [execution-owner: skill=orca-task-execution]
  [task-domain: software|reverse]
  [worker-role: terra|luna]

Derived profiles:
  software / terra -> codex / gpt-5.6-terra / xhigh
  software / luna  -> codex / gpt-5.6-luna  / max
  reverse  / terra -> codex / gpt-5.6-terra / max
  reverse  / luna  -> codex / gpt-5.6-luna  / max

This script rejects caller-supplied ownership, domain, role, profile, terminal,
and JSON options. The persisted Task route and launch receipt are authoritative.
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 2
}

need_value() {
  [ "$#" -ge 2 ] || die "$1 requires a value"
}

extract_task_launch_contract() {
  python3 - "$1" "$2" <<'PY'
import json
import re
import sys

path, wanted = sys.argv[1:]
with open(path, encoding="utf-8") as handle:
    data = json.load(handle)

def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)

specs = []
for item in walk(data):
    task_id = item.get("id", item.get("taskId", item.get("task_id")))
    spec = item.get("spec")
    if str(task_id) == wanted and isinstance(spec, str):
        specs.append(spec)

specs = list(dict.fromkeys(specs))
if len(specs) != 1:
    raise SystemExit(f"expected one full Task spec for {wanted!r}, found {len(specs)}")

lines = specs[0].splitlines()
if len(lines) < 3:
    raise SystemExit("Task is missing its three-line execution route")

patterns = (
    (r"\[execution-owner: skill=([^\s\]]+)\]", lines[0], "execution-owner"),
    (r"\[task-domain: ([^\s\]]+)\]", lines[1], "task-domain"),
    (r"\[worker-role: ([^\s\]]+)\]", lines[2], "worker-role"),
)
values = []
for pattern, line, name in patterns:
    match = re.fullmatch(pattern, line)
    if not match:
        raise SystemExit(f"Task has an invalid {name} line")
    values.append(match.group(1))

owner, domain, role = values
if owner != "orca-task-execution":
    raise SystemExit(f"Task execution owner must be orca-task-execution, got {owner!r}")

profiles = {
    ("software", "terra"): ("codex", "gpt-5.6-terra", "xhigh"),
    ("software", "luna"): ("codex", "gpt-5.6-luna", "max"),
    ("reverse", "terra"): ("codex", "gpt-5.6-terra", "max"),
    ("reverse", "luna"): ("codex", "gpt-5.6-luna", "max"),
}
profile = profiles.get((domain, role))
if profile is None:
    raise SystemExit(f"Task domain/role is not allowed: {domain!r}/{role!r}")

print("\t".join((*profile, owner, domain, role)))
PY
}

verify_launch_receipt() {
  python3 - "$1" "$2" "$3" "$4" <<'PY'
import json
import sys

path, expected_agent, expected_model, expected_effort = sys.argv[1:]
with open(path, encoding="utf-8") as handle:
    data = json.load(handle)

def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)

launches = []
for item in walk(data):
    launch = item.get("launch")
    if (
        isinstance(launch, dict)
        and isinstance(launch.get("requested"), dict)
        and isinstance(launch.get("effective"), dict)
    ):
        launches.append(launch)

if len(launches) != 1:
    raise SystemExit(
        "launch receipt must contain one requested/effective profile pair; "
        f"found {len(launches)}"
    )

def field(obj, *names):
    for name in names:
        value = obj.get(name)
        if value is not None:
            return str(value)
    return None

def profile(obj):
    return (
        field(obj, "agent", "agentId", "agent_id"),
        field(obj, "model", "modelId", "model_id"),
        field(obj, "effort", "reasoningEffort", "reasoning_effort"),
    )

expected = (expected_agent, expected_model, expected_effort)
requested = profile(launches[0]["requested"])
effective = profile(launches[0]["effective"])
if requested != expected:
    raise SystemExit(f"requested launch profile mismatch: expected {expected!r}, got {requested!r}")
if effective != expected:
    raise SystemExit(f"effective launch profile mismatch: expected {expected!r}, got {effective!r}")
PY
}

dispatch_tmp_dir=""
cleanup() {
  if [ -n "$dispatch_tmp_dir" ] && [ -d "$dispatch_tmp_dir" ]; then
    rm -f "$dispatch_tmp_dir/tasks.json" "$dispatch_tmp_dir/route.tsv" "$dispatch_tmp_dir/receipt.json" "$dispatch_tmp_dir/bad-receipt.json"
    rmdir "$dispatch_tmp_dir" 2>/dev/null || true
  fi
}
trap cleanup EXIT HUP INT TERM

run_self_test() {
  command -v python3 >/dev/null 2>&1 || die "python3 is required"
  dispatch_tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/orca-task-dispatch.XXXXXX")
  cat >"$dispatch_tmp_dir/tasks.json" <<'JSON'
{"ok":true,"result":{"tasks":[{"id":"ST","spec":"[execution-owner: skill=orca-task-execution]\n[task-domain: software]\n[worker-role: terra]\nTask: ST"},{"id":"SL","spec":"[execution-owner: skill=orca-task-execution]\n[task-domain: software]\n[worker-role: luna]\nTask: SL"},{"id":"RT","spec":"[execution-owner: skill=orca-task-execution]\n[task-domain: reverse]\n[worker-role: terra]\nTask: RT"},{"id":"RL","spec":"[execution-owner: skill=orca-task-execution]\n[task-domain: reverse]\n[worker-role: luna]\nTask: RL"},{"id":"BAD_OWNER","spec":"[execution-owner: skill=bn]\n[task-domain: reverse]\n[worker-role: terra]\nTask: BAD_OWNER"},{"id":"BAD_DOMAIN","spec":"[execution-owner: skill=orca-task-execution]\n[task-domain: mixed]\n[worker-role: terra]\nTask: BAD_DOMAIN"},{"id":"BAD_ROLE","spec":"[execution-owner: skill=orca-task-execution]\n[task-domain: software]\n[worker-role: coordinator]\nTask: BAD_ROLE"}]}}
JSON
  cat >"$dispatch_tmp_dir/receipt.json" <<'JSON'
{"ok":true,"result":{"launch":{"requested":{"agent":"codex","model":"gpt-5.6-terra","effort":"xhigh"},"effective":{"agent":"codex","model":"gpt-5.6-terra","effort":"xhigh"}}}}
JSON
  cat >"$dispatch_tmp_dir/bad-receipt.json" <<'JSON'
{"ok":true,"result":{"launch":{"requested":{"agent":"codex","model":"gpt-5.6-terra","effort":"xhigh"},"effective":{"agent":"codex","model":"gpt-5.6-terra","effort":"medium"}}}}
JSON

  [ "$(extract_task_launch_contract "$dispatch_tmp_dir/tasks.json" ST)" = $'codex\tgpt-5.6-terra\txhigh\torca-task-execution\tsoftware\tterra' ] || die "software/Terra route self-test failed"
  [ "$(extract_task_launch_contract "$dispatch_tmp_dir/tasks.json" SL)" = $'codex\tgpt-5.6-luna\tmax\torca-task-execution\tsoftware\tluna' ] || die "software/Luna route self-test failed"
  [ "$(extract_task_launch_contract "$dispatch_tmp_dir/tasks.json" RT)" = $'codex\tgpt-5.6-terra\tmax\torca-task-execution\treverse\tterra' ] || die "reverse/Terra route self-test failed"
  [ "$(extract_task_launch_contract "$dispatch_tmp_dir/tasks.json" RL)" = $'codex\tgpt-5.6-luna\tmax\torca-task-execution\treverse\tluna' ] || die "reverse/Luna route self-test failed"
  for bad in BAD_OWNER BAD_DOMAIN BAD_ROLE; do
    if extract_task_launch_contract "$dispatch_tmp_dir/tasks.json" "$bad" >/dev/null 2>&1; then
      die "$bad route rejection self-test failed"
    fi
  done

  verify_launch_receipt "$dispatch_tmp_dir/receipt.json" codex gpt-5.6-terra xhigh
  if verify_launch_receipt "$dispatch_tmp_dir/bad-receipt.json" codex gpt-5.6-terra xhigh >/dev/null 2>&1; then
    die "receipt mismatch self-test failed"
  fi
  printf 'self-test: ok\n'
}

if [ "${1:-}" = "--self-test" ]; then
  [ "$#" -eq 1 ] || die "--self-test accepts no other arguments"
  run_self_test
  exit 0
fi

task_id=""
run_id=""
worktree=""
forward_args=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --task)
      need_value "$@"
      task_id=$2
      shift 2
      ;;
    --run)
      need_value "$@"
      run_id=$2
      forward_args+=("--run" "$2")
      shift 2
      ;;
    --worktree)
      need_value "$@"
      worktree=$2
      forward_args+=("--worktree" "$2")
      shift 2
      ;;
    --on|--name|--repo|--base-branch|--display-name|--comment|--setup|--retry-of|--timeout-ms|--from|--retry-request)
      need_value "$@"
      forward_args+=("$1" "$2")
      shift 2
      ;;
    --execution-owner|--task-domain|--worker-role|--agent|--model|--effort|--terminal|--json)
      die "$1 is controlled by the persisted Task route or this script"
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "unsupported argument: $1"
      ;;
  esac
done

[ -n "$task_id" ] || die "--task is required"
[ -n "$worktree" ] || die "--worktree is required; terminal reuse is a separately verified path"
command -v python3 >/dev/null 2>&1 || die "python3 is required"

orca_cmd=()
if [ -n "${ORCA_CLI_COMMAND:-}" ]; then
  read -r -a orca_cmd <<<"$ORCA_CLI_COMMAND"
elif [ -n "${ORCA_DEV_REPO_ROOT:-}" ]; then
  orca_cmd=(orca-dev)
elif [ "$(uname -s)" = "Linux" ]; then
  orca_cmd=(orca-ide)
else
  orca_cmd=(orca)
fi
[ "${#orca_cmd[@]}" -gt 0 ] || die "could not resolve the Orca CLI command"
command -v "${orca_cmd[0]}" >/dev/null 2>&1 || die "Orca CLI not found: ${orca_cmd[0]}"

dispatch_tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/orca-task-dispatch.XXXXXX")
task_list_cmd=("${orca_cmd[@]}" orchestration task-list)
if [ -n "$run_id" ]; then
  task_list_cmd+=("--run" "$run_id")
fi
task_list_cmd+=(--json)

set +e
"${task_list_cmd[@]}" >"$dispatch_tmp_dir/tasks.json"
task_status=$?
set -e
if [ "$task_status" -ne 0 ]; then
  cat "$dispatch_tmp_dir/tasks.json"
  exit "$task_status"
fi

if ! extract_task_launch_contract "$dispatch_tmp_dir/tasks.json" "$task_id" >"$dispatch_tmp_dir/route.tsv"; then
  die "could not load an authoritative ownership/domain/role route for Task $task_id"
fi
IFS=$'\t' read -r profile_agent profile_model profile_effort execution_owner task_domain worker_role <"$dispatch_tmp_dir/route.tsv"
[ "$execution_owner" = "orca-task-execution" ] || die "Task execution owner is invalid"
[ -n "$profile_agent" ] && [ -n "$profile_model" ] && [ -n "$profile_effort" ] || die "derived Task profile is incomplete"
[ -n "$task_domain" ] && [ -n "$worker_role" ] || die "Task domain/role is incomplete"

worker_cmd=(
  "${orca_cmd[@]}" orchestration worker-start
  --task "$task_id"
  --agent "$profile_agent"
  --model "$profile_model"
  --effort "$profile_effort"
  "${forward_args[@]}"
  --json
)

set +e
"${worker_cmd[@]}" >"$dispatch_tmp_dir/receipt.json"
worker_status=$?
set -e
if [ "$worker_status" -ne 0 ]; then
  cat "$dispatch_tmp_dir/receipt.json"
  exit "$worker_status"
fi

if ! verify_launch_receipt "$dispatch_tmp_dir/receipt.json" "$profile_agent" "$profile_model" "$profile_effort"; then
  cat "$dispatch_tmp_dir/receipt.json"
  printf 'error: worker may be live, but its requested/effective derived profile was not proven; follow runtime recovery guidance\n' >&2
  exit 3
fi

cat "$dispatch_tmp_dir/receipt.json"
