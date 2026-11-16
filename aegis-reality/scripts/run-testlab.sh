#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
AEGIS_DIR="$ROOT_DIR/aegis-reality"
PROJECT_ID="${GOOGLE_CLOUD_PROJECT:-${GCLOUD_PROJECT:-}}"
RESULTS_BUCKET="${AEGIS_RESULTS_BUCKET:-}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Set GOOGLE_CLOUD_PROJECT to an authorized Google Cloud project." >&2
  exit 2
fi
for tool in gcloud python3; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Missing required tool: $tool" >&2; exit 2; }
done

"$ROOT_DIR/gradlew" -p "$ROOT_DIR" :aegis-reality:app:assembleDebug :aegis-reality:app:assembleDebugAndroidTest

APP_APK="$AEGIS_DIR/app/build/outputs/apk/debug/app-debug.apk"
TEST_APK="$AEGIS_DIR/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk"
[[ -f "$APP_APK" && -f "$TEST_APK" ]] || { echo "Expected APK outputs were not produced." >&2; exit 3; }

RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
WORK_DIR="$AEGIS_DIR/reports/$RUN_ID"
mkdir -p "$WORK_DIR"

# Fail closed: only exact model name + codename + PHYSICAL form + API 36 pass.
gcloud firebase test android models list --project="$PROJECT_ID" --format=json > "$WORK_DIR/model-catalog.json"
python3 "$AEGIS_DIR/device_catalog.py" "$WORK_DIR/model-catalog.json" --output "$WORK_DIR/approved-device-matrix.json"

while IFS=$'\t' read -r model_id codename; do
  [[ -n "$model_id" && -n "$codename" ]] || { echo "Invalid selected model entry." >&2; exit 4; }
  echo "Running on approved physical target: $codename ($model_id)"
  args=(
    firebase test android run
    "--project=$PROJECT_ID"
    "--type=instrumentation"
    "--app=$APP_APK"
    "--test=$TEST_APK"
    "--device=model=$model_id,version=36"
    "--timeout=15m"
    "--results-dir=aegis-reality/$RUN_ID/$codename"
    "--num-flaky-test-attempts=0"
  )
  if [[ -n "$RESULTS_BUCKET" ]]; then
    args+=("--results-bucket=$RESULTS_BUCKET")
  fi
  gcloud "${args[@]}"
done < <(python3 - "$WORK_DIR/approved-device-matrix.json" <<'PY'
import json, sys
for item in json.load(open(sys.argv[1], encoding="utf-8")):
    print(f"{item['model_id']}\t{item['expected_codename']}")
PY
)

echo "Test Lab runs submitted. Review the Firebase Test Lab results and retain the catalog + matrix in $WORK_DIR."
