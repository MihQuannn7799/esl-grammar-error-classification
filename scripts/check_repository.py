"""Check the public repository without training models or changing files.

Run from a Git checkout: python scripts/check_repository.py
Only Git-tracked or non-ignored candidate files are inspected. Local environments
and ignored experiment outputs are outside the publication check.
"""
from __future__ import annotations

import ast
import csv
import importlib.util
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def public_paths() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, check=True,
    )
    return sorted({ROOT / name for name in result.stdout.decode("utf-8").split("\0") if name})


def check(paths: list[Path]) -> dict[str, int]:
    errors = []
    markdown_links = 0
    csv_files = 0
    modules = {}
    for path in paths:
        relative = path.relative_to(ROOT)
        if not path.is_file():
            errors.append(f"Missing public file: {relative.as_posix()}")
            continue
        if relative.parts[0] in {"data", "data_set", "reports", "runs", ".cache", ".venv"}:
            errors.append(f"Research/local artifact in publication: {relative.as_posix()}")
        if "private" in relative.parts or relative.as_posix().startswith("src/reporting/"):
            errors.append(f"Excluded directory in publication: {relative.as_posix()}")
        if path.suffix.lower() in {".pdf", ".docx", ".pptx", ".pt", ".pth", ".sgml", ".safetensors", ".zip", ".pem", ".key"}:
            errors.append(f"Excluded artifact type: {relative.as_posix()}")
        if path.suffix == ".md":
            text = path.read_text(encoding="utf-8-sig")
            for target in re.findall(r"\]\(([^)\n]+)\)", text):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                local_target = target.split("#", 1)[0].strip("<>")
                markdown_links += 1
                if not (path.parent / local_target).exists():
                    errors.append(f"Broken link in {relative.as_posix()}: {target}")
        if relative.parts[0] == "results" and path.suffix == ".csv":
            with path.open(encoding="utf-8-sig", newline="") as stream:
                fields = set(csv.DictReader(stream).fieldnames or [])
            forbidden = {"sample_id", "annotation_id", "essay_id", "sentence", "error_span", "correction"}
            if fields & forbidden:
                errors.append(f"Row-level fields in aggregate CSV: {relative.as_posix()}")
            csv_files += 1
        if path.suffix == ".py":
            parts = list(relative.with_suffix("").parts)
            if parts[-1] == "__init__":
                parts.pop()
            modules[".".join(parts)] = (path, ast.parse(path.read_bytes()))
    for module, (path, tree) in modules.items():
        package = module if path.name == "__init__.py" else module.rsplit(".", 1)[0]
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                name = node.module or ""
                if node.level:
                    name = importlib.util.resolve_name("." * node.level + name, package)
                imports = [name]
            else:
                continue
            for name in imports:
                if (name == "src" or name.startswith("src.")) and name not in modules:
                    errors.append(f"Unresolved local import in {module}: {name}")
    if errors:
        raise ValueError("\n".join(errors))
    return {"files": len(paths), "python_modules": len(modules),
            "local_markdown_links": markdown_links, "aggregate_csvs": csv_files}


def main() -> int:
    try:
        counts = check(public_paths())
    except (ValueError, OSError, SyntaxError, subprocess.CalledProcessError) as exc:
        print(f"Repository checks failed:\n{exc}", file=sys.stderr)
        return 1
    print("Repository checks passed: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
