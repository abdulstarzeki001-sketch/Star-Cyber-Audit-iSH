"""Safe, local-only file inventory shared by Phase 1 checkers."""
from pathlib import Path
import os

SOURCE_SUFFIXES = {
    ".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx",
    ".sh", ".json", ".yml", ".yaml", ".md", ".txt", ".html",
    ".css", ".toml", ".ini", ".cfg", ".env"
}
ALWAYS_SKIP = {".git", "node_modules", ".venv", "venv", "__pycache__",
               ".pytest_cache", ".mypy_cache", "dist", "build",
               "reports", "downloads", "offline_samples", "coverage"}
EVIDENCE_DIRS = {"research", "reviews"}
MAX_FILES = 5000
MAX_BYTES = 1_000_000


def project_files(root, include_evidence=False, max_files=MAX_FILES):
    """Yield bounded regular files; never follow links or leave root.

    Archive folders are excluded by default, not deleted. Set
    include_evidence=True for an explicitly requested offline archive scan.
    """
    root = Path(root).expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("root must be a directory")
    count = 0
    for parent, dirs, files in os.walk(root, followlinks=False):
        base = Path(parent)
        safe_dirs = []
        for name in sorted(dirs):
            path = base / name
            if (name in ALWAYS_SKIP or
                    (not include_evidence and name in EVIDENCE_DIRS) or
                    (name.startswith(".") and name != ".github") or
                    path.is_symlink()):
                continue
            safe_dirs.append(name)
        dirs[:] = safe_dirs
        for name in sorted(files):
            path = base / name
            if (name.startswith(".") and name not in (".env", ".env.local", ".gitignore")
                    and path.suffix.lower() != ".env"):
                continue
            if path.is_symlink() or not path.is_file():
                continue
            if path.suffix.lower() not in SOURCE_SUFFIXES and name != ".gitignore":
                continue
            try:
                path.resolve(strict=True).relative_to(root)
                size = path.stat().st_size
            except (OSError, ValueError):
                continue
            count += 1
            if count > max_files:
                raise ValueError("file limit exceeded; narrow the scan scope")
            if size <= MAX_BYTES:
                yield path


def numbered_lines(path):
    """Return decoded text lines without interpreting or executing the file."""
    try:
        raw = Path(path).read_bytes()
    except OSError:
        return []
    if b"\x00" in raw[:4096]:
        return []
    return raw.decode("utf-8", errors="replace").splitlines()


def save_report(report, destination):
    """Save JSON, creating only the requested output directory."""
    import json
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
