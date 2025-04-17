import os
import re
import argparse
import subprocess
from pathlib import Path

# Paths
project_dir = Path(__file__).resolve().parent
version_file = project_dir / "geedl" / "__version__.py"

# Parse CLI arguments
parser = argparse.ArgumentParser()
parser.add_argument("--release", action="store_true", help="Publish to PyPI and tag Git")
args = parser.parse_args()

# Read current version
version_text = version_file.read_text(encoding="utf-8")
match = re.search(r'__version__\s*=\s*"(.+?)"', version_text)
current_version = match.group(1) if match else "0.0.0"

if args.release:
    # Bump patch version
    major, minor, patch = map(int, current_version.split("."))
    new_version = f"{major}.{minor}.{patch + 1}"

    # Update version file
    new_text = re.sub(r'__version__\s*=\s*".+?"',
                      f'__version__ = "{new_version}"',
                      version_text)
    version_file.write_text(new_text, encoding="utf-8")
    print(f"Version bumped: {current_version} → {new_version}")
else:
    # Test mode, no version bump, just use the current version
    new_version = current_version
    print(f"Test mode: no version bump. Using {new_version}")

# Git add & commit
subprocess.run("git add -A", shell=True)
commit_msg = f"Release v{new_version}" if args.release else f"Test commit (v{new_version})"
subprocess.run(f'git commit -m "{commit_msg}"', shell=True)
subprocess.run("git push", shell=True)

if args.release:
    # Clean old builds
    for folder in ["build", "dist", "geedl.egg-info"]:
        if Path(folder).exists():
            subprocess.run(["rmdir", "/s", "/q", folder], shell=True)

    # Build and upload to PyPI
    subprocess.run("python setup.py sdist bdist_wheel", shell=True)
    subprocess.run("twine upload dist/*", shell=True)

    # Tag and push tag to Git
    subprocess.run(f"git tag v{new_version}", shell=True)
    subprocess.run("git push origin --tags", shell=True)
    print("Release complete.")
else:
    print("Test commit complete (no PyPI upload, no tag).")
