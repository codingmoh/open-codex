import dagger
import os
import re

PROJECT_DIR = "/src/open-codex"
BREW_REPO_URL = "https://github.com/codingmoh/homebrew-open-codex.git"
FORMULA_PATH = "Formula/open-codex.rb"

async def get_current_version(pyproject_path):
    with open(pyproject_path, "r") as f:
        content = f.read()
    match = re.search(r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', content)
    if match:
        major, minor, patch = map(int, match.groups())
        return f"{major}.{minor}.{patch}", (major, minor, patch)
    raise ValueError("Version not found")

async def bump_minor_version(pyproject_path):
    version_str, (major, minor, patch) = await get_current_version(pyproject_path)
    new_version = f"{major}.{minor + 1}.0"
    with open(pyproject_path, "r") as f:
        content = f.read()
    content = re.sub(r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', f'version = "{new_version}"', content)
    with open(pyproject_path, "w") as f:
        f.write(content)
    return new_version

async def main():
    async with dagger.Connection() as client:
        src = client.host().directory(".")
        py = (
            client.container()
            .from_("python:3.11")
            .with_mounted_directory(PROJECT_DIR, src)
            .with_workdir(PROJECT_DIR)
            .with_exec(["pip", "install", "build", "twine"])
        )

        version = await bump_minor_version("pyproject.toml")
        await py.with_exec(["python", "-m", "build"])

        dist_files = await src.file("dist").entries()
        tar_gz = next(f for f in dist_files if f.endswith(".tar.gz"))
        tar_path = f"dist/{tar_gz}"

        # Compute SHA256 hash
        sha_out = await py.with_exec(["shasum", "-a", "256", tar_path]).stdout()
        sha256 = sha_out.split()[0]

        # Clone Homebrew repo
        brew_dir = client.git(BREW_REPO_URL).branch("master").tree()
        formula = await brew_dir.file(FORMULA_PATH).contents()
        formula = re.sub(r'url ".*"', f'url "https://files.pythonhosted.org/packages/source/o/open-codex/{tar_gz}"', formula)
        formula = re.sub(r'sha256 ".*"', f'sha256 "{sha256}"', formula)

        # Write updated formula
        updated_brew = client.host().directory("homebrew-updated", include=["."])
        formula_file = updated_brew.file(FORMULA_PATH)
        await formula_file.write(formula)

        print("✅ Version bumped, package built, and Homebrew formula updated!")
        print(f"New version: {version}")
        print(f"SHA256: {sha256}")
        print(f"Tarball: {tar_gz}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())