from __future__ import annotations

import json
from pathlib import Path

import pytest

from colorado_flow.io import load_config


def test_full_latex_assets_manifest():
    cfg = load_config()
    full_dir = Path(cfg["_root_dir"]) / "latex_full"
    manifest_path = full_dir / "generated" / "assets_manifest.json"
    if not manifest_path.exists():
        pytest.skip("Chưa chạy stage export")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["run_id"] == "run-20261024T160504+0000"
    assert len(manifest["tables"]) >= 14
    assert len(manifest["figures"]) >= 14
    for relative in manifest["tables"] + manifest["figures"]:
        assert (full_dir / relative).is_file(), relative
    assert (full_dir / "generated" / "numbers.tex").is_file()
    assert (full_dir / "metadata.tex").is_file()
