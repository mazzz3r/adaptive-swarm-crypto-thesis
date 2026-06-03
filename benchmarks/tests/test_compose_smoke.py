import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.docker_smoke
@pytest.mark.skipif(os.environ.get("RUN_DOCKER_SMOKE") != "1", reason="set RUN_DOCKER_SMOKE=1 to enable docker smoke tests")
def test_compose_stable_scenario(tmp_path: Path) -> None:
    result = subprocess.run(
        ["uv", "run", "bench", "run", "--scenario", "scenarios/stable.yaml", "--output-dir", str(tmp_path)],
        cwd=Path(__file__).resolve().parents[1],
        check=True,
        capture_output=True,
        text=True,
    )
    output_dir = Path(result.stdout.strip().splitlines()[-1])
    assert (output_dir / "summary.csv").exists()
    assert (output_dir / "summary.json").exists()
