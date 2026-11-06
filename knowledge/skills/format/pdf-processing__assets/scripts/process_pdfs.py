#!/usr/bin/env python3
"""Verify, recoverably deduplicate, and normalize a task PDF library."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
from datetime import datetime
from pathlib import Path


def is_pdf(path: Path) -> bool:
    """Return whether a file has the required PDF signature."""
    try:
        with path.open("rb") as handle:
            return handle.read(4) == b"%PDF"
    except OSError:
        return False


def sha256(path: Path) -> str:
    """Return the SHA-256 digest for one file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_stem(stem: str) -> str:
    """Create a readable, portable filename stem without changing its meaning."""
    cleaned = re.sub(r"[\\\\/:*?\"<>|\x00-\x1f]+", "_", stem).strip(" ._")
    return cleaned[:120] or "untitled"


def unique_destination(directory: Path, stem: str, suffix: str) -> Path:
    """Choose a path that does not overwrite an existing file."""
    candidate = directory / f"{stem}{suffix}"
    index = 1
    while candidate.exists():
        candidate = directory / f"{stem}_{index}{suffix}"
        index += 1
    return candidate


def move_recoverably(source: Path, destination_dir: Path) -> Path:
    """Move a file to a recovery directory without overwriting another file."""
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = unique_destination(destination_dir, safe_stem(source.stem), source.suffix.lower())
    return Path(shutil.move(str(source), str(destination)))


def main() -> None:
    """Process a PDF directory and write a Markdown report."""
    parser = argparse.ArgumentParser(description="Verify and recoverably deduplicate PDFs")
    parser.add_argument("pdf_dir", help="Directory containing downloaded PDFs")
    parser.add_argument("--report-dir", default=None, help="Directory for the Markdown report")
    args = parser.parse_args()

    pdf_dir = Path(args.pdf_dir).expanduser().resolve()
    report_dir = Path(args.report_dir).expanduser().resolve() if args.report_dir else pdf_dir.parent
    if not pdf_dir.is_dir():
        raise SystemExit(f"PDF directory does not exist: {pdf_dir}")
    report_dir.mkdir(parents=True, exist_ok=True)

    duplicates_dir = pdf_dir / "duplicates"
    rejected_dir = pdf_dir / "rejected"
    files = sorted(path for path in pdf_dir.iterdir() if path.is_file())
    hashes: dict[str, Path] = {}
    valid: list[Path] = []
    rejected: list[tuple[Path, Path]] = []
    duplicates: list[tuple[Path, Path]] = []
    renamed: list[tuple[Path, Path]] = []

    for path in files:
        if not is_pdf(path):
            destination = move_recoverably(path, rejected_dir)
            rejected.append((path, destination))
            continue
        digest = sha256(path)
        canonical = hashes.get(digest)
        if canonical is not None:
            destination = move_recoverably(path, duplicates_dir)
            duplicates.append((path, destination))
            continue
        desired = pdf_dir / f"{safe_stem(path.stem)}.pdf"
        if desired != path:
            destination = desired if not desired.exists() else unique_destination(pdf_dir, safe_stem(path.stem), ".pdf")
            path.rename(destination)
            renamed.append((path, destination))
            path = destination
        hashes[digest] = path
        valid.append(path)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"pdf_processing_report_{timestamp}.md"
    lines = [
        "# PDF Processing Report",
        "",
        f"- Time: {datetime.now().isoformat(timespec='seconds')}",
        f"- PDF directory: {pdf_dir}",
        f"- Valid unique PDFs: {len(valid)}",
        f"- Rejected non-PDF files: {len(rejected)}",
        f"- Recoverable duplicates: {len(duplicates)}",
        f"- Normalized filenames: {len(renamed)}",
        "",
        "## Valid PDFs",
    ]
    if valid:
        lines.extend(f"- {path.relative_to(pdf_dir)}" for path in valid)
    else:
        lines.append("- None")
    lines.extend(["", "## Rejected files"])
    if rejected:
        lines.extend(f"- {source.name} -> {destination.relative_to(pdf_dir)} (missing %PDF header)" for source, destination in rejected)
    else:
        lines.append("- None")
    lines.extend(["", "## Duplicate files"])
    if duplicates:
        lines.extend(f"- {source.name} -> {destination.relative_to(pdf_dir)}" for source, destination in duplicates)
    else:
        lines.append("- None")
    lines.extend(["", "## Renamed files"])
    if renamed:
        lines.extend(f"- {source.name} -> {destination.name}" for source, destination in renamed)
    else:
        lines.append("- None")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Verified unique PDFs: {len(valid)}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
