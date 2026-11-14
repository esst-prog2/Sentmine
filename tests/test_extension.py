"""open-in-sentmine: the browser extension's own tests (node), and its manifest."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

EXTENSION = Path(__file__).parent.parent / "extension"


@pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")
def test_the_extensions_logic():
    run = subprocess.run(["node", "--test", str(EXTENSION / "test" / "logic.test.mjs")],
                         capture_output=True, text=True, timeout=120, stdin=subprocess.DEVNULL)
    assert run.returncode == 0, run.stdout + run.stderr


def test_the_extension_asks_for_little():
    manifest = json.loads((EXTENSION / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["manifest_version"] == 3
    assert sorted(manifest["permissions"]) == ["activeTab", "contextMenus", "scripting", "sidePanel"]
    assert manifest["host_permissions"] == ["http://127.0.0.1/*"]   # sentmine's address, never all websites
