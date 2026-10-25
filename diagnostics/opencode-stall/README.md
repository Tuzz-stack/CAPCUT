# Isolated native OpenCode subprocess diagnostic

This branch contains a synthetic diagnostic only. It does not change this repository's plugin, release workflow, or any product implementation.

The engine is the public `opencode-linux-x64@1.18.23` ELF with SHA-256 `de0724a36eaf3166e7f1ff38d0f4478b95ccc47725e9597b3fe66d3d3e18baa2`. The base image is pinned by digest. A local deterministic SSE server instructs real native bash/Git tools, writes only synthetic files, and records terminal tool states, HTTP health, and child process states. The 8,219 catalog records are generated artificial metadata, not an exported provider configuration. No real model, cloud sandbox, repository credential, or private project is used.

Each probe shares an isolated network-none/PID namespace between one Python observer and the engine container. Containers have bounded CPU, memory, PID count and runtime; only their temporary data is writable. The observer has SYS_PTRACE for diagnostic reads, the engine does not. No engine patch or runtime upgrade is made. Some kernel stack reads may remain unavailable and are recorded as such.

The CI is push-triggered only on `codex/opencode-native-x64-diagnostic-20261025`, uses a standard Ubuntu x64 runner and read-only checkout credentials (not persisted), and retains its small diagnostic artifact for one day. It does not publish a release or call the existing plugin publishing workflow.

Native test:

```text
python3 diagnostics/opencode-stall/prepare.py
python3 diagnostics/opencode-stall/matrix.py --host-kind native-x64 --repeats 3 --output /tmp/native-stall-evidence
```

The exact pinned images must be pulled before execution, as shown in the workflow. On an ARM Mac with the already cached native ARM Python observer, use `--host-kind rosetta` for the matching x64 engine comparison. Check the two sides' engine/config/source hashes and initial Git OID. The host kernel, filesystem integration and observer architecture still differ; this is an environment comparison, not proof that every difference is caused by the CPU translator.

The synthetic case must also reproduce the original class of failure locally before a passing native test can meaningfully isolate its cause. A passing batch never proves absence of a low-frequency engine bug. No fix is included here.
