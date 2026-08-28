#!/usr/bin/env bash
set -euo pipefail

# Start one fresh supervised worker from the profile persisted on the Task's
# first line. Refuse caller-supplied profile overrides and verify Orca's launch
# receipt before reporting success.

usage() {
  cat <<'EOF'
Usage:
  dispatch_profiled_worker.sh --task <task_id> --worktree <selector> [worker-start placement options]
  dispatch_profiled_worker.sh --self-test

Required:
  --task <id>                 Existing Orca orchestration Task
  --worktree <selector>       current, exact existing selector, new-child, or new-top-level

Forwarded when present:
  --run --on --name --repo --base-branch --display-name --comment --setup
  --retry-of --timeout-ms --from --retry-request

The Task spec must start with exactly:
  [worker-profile: agent=<agent> model=<model> effort=<effort>]

Allowed profiles for orca-software-development:
  codex / gpt-5.6-terra / xhigh
  codex / gpt-5.6-luna  / max

This script intentionally rejects --agent, --model, --effort, --terminal, and
--json. The persisted Task profile and JSON receipt are authoritative.
EOF
}

die() {
  printf 'error: %s\n' "$*" >&2
  exit 2
}

need_value() {
  [ "$#" -ge 2 ] || die "$1 requires a value"
}

extract_task_profile() {
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
first = lines[0] if lines else ""
match = re.fullmatch(
    r"\[worker-profile: agent=([^\s\]]+) model=([^\s\]]+) effort=([^\s\]]+)\]",
    first,
)
if not match:
    raise SystemExit("Task first line is missing or has an invalid worker-profile")

print("\t".join(match.groups()))
PY
}

assert_allowed_profile() {
  case "$1 $2 $3" in
    "codex gpt-5.6-terra xhigh"|"codex gpt-5.6-luna max")
      return 0
      ;;
    *)
      printf 'error: profile is not allowed for orca-software-development: agent=%s model=%s effort=%s\n' "$1" "$2" "$3" >&2
      printf 'allowed: codex/gpt-5.6-terra/xhigh, codex/gpt-5.6-luna/max\n' >&2
      return 1
      ;;
  esac
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
    if isinstance(launch, dict) and isinstance(launch.get("requested"), dict) and isinstance(launch.get("effective"), dict):
        launches.append(launch)

if len(launches) != 1:
    raise SystemExit(f"launch receipt must contain one requested/effective profile pair; found {len(launches)}")

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

profiled_tmp_dir=""
cleanup() {
  if [ -n "$profiled_tmp_dir" ] && [ -d "$profiled_tmp_dir" ]; then
    rm -f "$profiled_tmp_dir/tasks.json" "$profiled_tmp_dir/profile.tsv" "$profiled_tmp_dir/receipt.json" "$profiled_tmp_dir/bad-receipt.json"
    rmdir "$profiled_tmp_dir" 2>/dev/null || true
  fi
}
trap cleanup EXIT HUP INT TERM

run_self_test() {
  command -v python3 >/dev/null 2>&1 || die "python3 is required"
  profiled_tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/orca-profiled-worker.XXXXXX")
  cat >"$profiled_tmp_dir/tasks.json" <<'JSON'
{"ok":true,"result":{"tasks":[{"id":"T1","spec":"[worker-profile: agent=codex model=gpt-5.6-terra effort=xhigh]\nTask: T1"}]}}
JSON
  cat >"$profiled_tmp_dir/receipt.json" <<'JSON'
{"ok":true,"result":{"launch":{"requested":{"agent":"codex","model":"gpt-5.6-terra","effort":"xhigh"},"effective":{"agent":"codex","model":"gpt-5.6-terra","effort":"xhigh"}}}}
JSON
  cat >"$profiled_tmp_dir/bad-receipt.json" <<'JSON'
{"ok":true,"result":{"launch":{"requested":{"agent":"codex","model":"gpt-5.6-terra","effort":"xhigh"},"effective":{"agent":"codex","model":"gpt-5.6-terra","effort":"medium"}}}}
JSON
  profile=$(extract_task_profile "$profiled_tmp_dir/tasks.json" T1)
  [ "$profile" = $'codex\tgpt-5.6-terra\txhigh' ] || die "profile parser self-test failed"
  assert_allowed_profile codex gpt-5.6-terra xhigh
  assert_allowed_profile codex gpt-5.6-luna max
  if assert_allowed_profile codex gpt-5.6-terra medium >/dev/null 2>&1; then
    die "profile allowlist self-test failed"
  fi
  verify_launch_receipt "$profiled_tmp_dir/receipt.json" codex gpt-5.6-terra xhigh
  if verify_launch_receipt "$profiled_tmp_dir/bad-receipt.json" codex gpt-5.6-terra xhigh >/dev/null 2>&1; then
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
    --agent|--model|--effort|--terminal|--json)
      die "$1 is controlled by the persisted Task profile or by this script"
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

profiled_tmp_dir=$(mktemp -d "${TMPDIR:-/tmp}/orca-profiled-worker.XXXXXX")
task_list_cmd=("${orca_cmd[@]}" orchestration task-list)
if [ -n "$run_id" ]; then
  task_list_cmd+=("--run" "$run_id")
fi
task_list_cmd+=(--json)

set +e
"${task_list_cmd[@]}" >"$profiled_tmp_dir/tasks.json"
task_status=$?
set -e
if [ "$task_status" -ne 0 ]; then
  cat "$profiled_tmp_dir/tasks.json"
  exit "$task_status"
fi

if ! extract_task_profile "$profiled_tmp_dir/tasks.json" "$task_id" >"$profiled_tmp_dir/profile.tsv"; then
  die "could not load an authoritative worker profile for Task $task_id"
fi
IFS=$'\t' read -r profile_agent profile_model profile_effort <"$profiled_tmp_dir/profile.tsv"
[ -n "$profile_agent" ] && [ -n "$profile_model" ] && [ -n "$profile_effort" ] || die "Task profile is incomplete"
assert_allowed_profile "$profile_agent" "$profile_model" "$profile_effort" || exit 2

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
"${worker_cmd[@]}" >"$profiled_tmp_dir/receipt.json"
worker_status=$?
set -e
if [ "$worker_status" -ne 0 ]; then
  cat "$profiled_tmp_dir/receipt.json"
  exit "$worker_status"
fi

if ! verify_launch_receipt "$profiled_tmp_dir/receipt.json" "$profile_agent" "$profile_model" "$profile_effort"; then
  cat "$profiled_tmp_dir/receipt.json"
  printf 'error: worker may be live, but its requested/effective profile was not proven; follow the receipt recovery guidance\n' >&2
  exit 3
fi

cat "$profiled_tmp_dir/receipt.json"
