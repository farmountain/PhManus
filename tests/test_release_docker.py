import subprocess
from pathlib import Path

import pytest


SCRIPT = Path("scripts/build-release-image.sh")


def test_dockerfile_exists():
    assert Path("Dockerfile.release").exists()


@pytest.mark.sit
def test_dry_run(monkeypatch, capfd):
    monkeypatch.setenv("DOCKER_DRYRUN", "1")
    subprocess.run(["bash", str(SCRIPT)], check=True)
    out = capfd.readouterr().out
    assert "Dockerfile.release" in out


@pytest.mark.uat
def test_custom_tag(monkeypatch, capfd):
    monkeypatch.setenv("DOCKER_DRYRUN", "1")
    subprocess.run(["bash", str(SCRIPT), "mytag"], check=True)
    out = capfd.readouterr().out
    assert "mytag" in out
