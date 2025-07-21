import os
import subprocess
from pathlib import Path
import pytest

SCRIPT = Path("scripts/build-release-image.sh")

def test_dockerfile_exists():
    assert Path("Dockerfile.release").exists()

@pytest.mark.sit
def test_dry_run(monkeypatch, capsys):
    monkeypatch.setenv("DOCKER_DRYRUN", "1")
    subprocess.run(["bash", str(SCRIPT)], check=True)
    out = capsys.readouterr().out
    assert "Dockerfile.release" in out

@pytest.mark.uat
def test_custom_tag(monkeypatch, capsys):
    monkeypatch.setenv("DOCKER_DRYRUN", "1")
    subprocess.run(["bash", str(SCRIPT), "mytag"], check=True)
    out = capsys.readouterr().out
    assert "mytag" in out
