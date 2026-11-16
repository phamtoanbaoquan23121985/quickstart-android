# AEGIS-Ω REALITY — Firebase Test Lab adapter

This directory adds a **real-device Android test lane** to the existing Firebase Android Quickstarts repository. It does not alter or replace the Firebase sample applications.

## Service lifecycle notice

Google currently documents Firebase Test Lab as deprecated, with shutdown scheduled for **September 30, 2027**. This integration is therefore a near-term real-device execution lane, not a long-term platform dependency. Keep the device-catalog and test-runner boundaries portable so the backend can migrate to Google Cloud Developer Device Platform before shutdown. See the [Google Cloud migration notice](https://docs.cloud.google.com/sdk/gcloud/reference/firebase/test/android).

## Initial supported targets

Only these user-authorized targets are eligible:

| Product name | Expected Android codename | Android API |
|---|---|---:|
| Pixel 10 Pro | `blazer` | 36 |
| Pixel 10 Pro XL | `mustang` | 36 |

The runner queries the live Firebase Test Lab model catalog and fails closed unless it finds exactly one entry for each exact product name, the expected codename, `PHYSICAL` form, and API 36 support. If Google's current catalog uses a different name/schema or either device is unavailable, the run stops rather than substituting an emulator or another Pixel.

**Important:** availability is not assumed. The catalog check performed at execution time is authoritative for whether Test Lab currently offers the requested physical device/API combination.

## What the first test lane covers

- Device identity and Android API-level scope gate.
- Minimal build identity collection (fingerprint, model, manufacturer, API); no serial number, IMEI, account, key, or secret collection.
- Runtime permission baseline: a permission not requested by the harness remains denied.
- A private secondary-process Messenger/Binder round trip, recording process separation and UID equality for this harness.

These are baseline tests of the harness and Android app-level security surfaces. They are **not vulnerability claims** and do not by themselves establish an Android framework, Binder, Permission Controller, Titan M2, TEE, or pKVM vulnerability.

## Run

Prerequisites:

- Google Cloud project with Firebase Test Lab enabled and billing/quotas configured as required by Google.
- `gcloud` authenticated with permission to run Firebase Test Lab tests.
- Android SDK/Gradle prerequisites for this repository.
- `GOOGLE_CLOUD_PROJECT` (or `GCLOUD_PROJECT`) set to the project ID.
- Optional: `AEGIS_RESULTS_BUCKET` for a Cloud Storage results bucket.

From the repository root:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export AEGIS_RESULTS_BUCKET="your-test-results-bucket" # optional
bash aegis-reality/scripts/run-testlab.sh
```

The script builds the harness APKs, downloads the current Test Lab model catalog through `gcloud`, validates the exact physical targets, and runs instrumentation tests separately on each approved device.

## Evidence and interpretation

Keep the generated catalog and approved matrix with the Test Lab run URLs/results. A valid device run must independently confirm `Build.DEVICE` is `blazer` or `mustang` as expected and `SDK_INT == 36`.

Evidence records must distinguish:

- `OBSERVED`: directly returned by a real device or Test Lab execution.
- `DOCUMENTED`: supported by official platform documentation.
- `NOT_ACCESSIBLE`: unavailable through the Test Lab app/test interface.
- `NOT_TESTED`: no valid test was run.
- `INFERRED`: hypothesis only; never report as a confirmed finding.

Test Lab provides an app-level instrumentation environment. It does not grant raw SPI/APDU access, Titan M2 firmware execution, Secure Element debug access, TEE internals, hypervisor control, or pKVM memory introspection. A Test Lab pass/fail must never be represented as proof of Titan M2 or pKVM compromise. Those domains require separate, explicitly authorized hardware-level evidence.

## Current implementation boundary

This is the first integration slice: a scoped instrumentation app, real-device catalog gate, and repeatable Test Lab invocation. It does not yet install and exercise every Firebase Quickstart sample, automate security-policy mutations, or collect privileged hardware evidence. Physical-device execution is pending an authorized Google Cloud project and a live catalog check.
