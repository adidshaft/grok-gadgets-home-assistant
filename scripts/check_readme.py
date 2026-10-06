"""Run the README Quickstart and compare the probe output with the README's JSON.

    python3 scripts/check_readme.py

CI runs it in a fresh checkout. Fixture only: no home, account or token.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    readme = (ROOT / "README.md").read_text()
    section = readme.split("## Quickstart", 1)[1].split("\n## ", 1)[0]
    commands = re.search(r"```sh\n(.*?)```", section, re.S)[1]
    # This checkout is the clone: skip the README's clone and cd lines.
    commands = "\n".join(
        line for line in commands.splitlines() if not line.startswith(("git clone", "cd "))
    )
    expected = json.loads(re.search(r"```json\n(.*?)```", section, re.S)[1])
    output = subprocess.run(
        ["bash", "-euo", "pipefail", "-c", commands],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    actual = json.loads(output[output.index("{") :])
    wrong = {k: (v, actual.get(k)) for k, v in expected.items() if actual.get(k) != v}
    if wrong:
        raise SystemExit(f"README Quickstart output differs (expected, actual): {wrong}")
    print(f"README Quickstart passed: {len(expected)} documented fields match (fixture only).")


if __name__ == "__main__":
    sys.exit(main())
