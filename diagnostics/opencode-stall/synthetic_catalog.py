"""Artificial public metadata only; no real provider configuration or credentials."""

def models():
    return {
        f"synthetic-{i:05d}": {
            "name": f"Synthetic diagnostic model {i:05d}",
            "provider_name": "Synthetic diagnostic provider",
            "released": "2026-01-01", "release_date": "2026-01-01",
            "last_updated": "2026-01-01", "knowledge": "2025-01",
            "family": "synthetic", "reasoning": True,
            "reasoning_options": ["none", "low", "high", "max"],
            "tool_call": True, "attachment": True, "temperature": True,
            "structured_output": True, "open_weights": True,
            "modalities": {"input": ["text", "image"], "output": ["text"]},
            "limit": {"context": 128000, "output": 8192},
            "cost": {"input": 0, "output": 0, "cache_read": 0},
            "description": "Artificial metadata for isolated subprocess diagnostics. " * 3,
            "variants": {x: {"reasoningEffort": x} for x in ["none", "low", "high", "max"]},
        }
        for i in range(8219)
    }
