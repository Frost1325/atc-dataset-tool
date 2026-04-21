from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

DEFAULT_EXTENSIONS = [
    ".aac",
    ".mp3",
    ".m4a",
    ".wav",
    ".flac",
    ".ogg",
    ".opus",
    ".wma",
    ".mp4",
    ".webm",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recursively convert common audio files to wav in place."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Root folder to search recursively. Defaults to current directory.",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=DEFAULT_EXTENSIONS,
        help="File extensions to match. Defaults to common audio formats.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing wav files.",
    )
    parser.add_argument(
        "--ffmpeg",
        default="ffmpeg",
        help="Path to ffmpeg executable. Defaults to ffmpeg in PATH.",
    )
    return parser.parse_args()


def normalize_extensions(extensions: list[str]) -> set[str]:
    normalized = set()
    for ext in extensions:
        ext = ext.strip().lower()
        if not ext:
            continue
        if not ext.startswith("."):
            ext = f".{ext}"
        normalized.add(ext)
    return normalized


def find_audio_files(root: Path, extensions: set[str]) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in extensions
    )


def convert_file(source: Path, target: Path, ffmpeg_cmd: str, overwrite: bool) -> None:
    command = [
        ffmpeg_cmd,
        "-y" if overwrite else "-n",
        "-i",
        str(source),
        str(target),
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def main() -> int:
    args = parse_args()
    root = Path(args.root).expanduser().resolve()
    extensions = normalize_extensions(args.extensions)

    if not root.exists():
        print(f"[ERROR] Folder does not exist: {root}")
        return 1

    if shutil.which(args.ffmpeg) is None and not Path(args.ffmpeg).exists():
        print(
            f"[ERROR] ffmpeg not found: {args.ffmpeg}\n"
            "Please install ffmpeg or pass --ffmpeg with the executable path."
        )
        return 1

    files = find_audio_files(root, extensions)
    if not files:
        print(f"[INFO] No matching files found under: {root}")
        return 0

    print(f"[INFO] Matching extensions: {', '.join(sorted(extensions))}")

    success_count = 0
    skipped_count = 0
    failed_count = 0

    for source in files:
        target = source.with_suffix(".wav")
        if target.exists() and not args.overwrite:
            print(f"[SKIP] {target} already exists")
            skipped_count += 1
            continue

        try:
            convert_file(source, target, args.ffmpeg, args.overwrite)
            print(f"[OK] {source} -> {target}")
            success_count += 1
        except subprocess.CalledProcessError as exc:
            error_output = exc.stderr.decode("utf-8", errors="ignore").strip()
            print(f"[FAIL] {source}")
            if error_output:
                print(error_output)
            failed_count += 1

    print(
        "\nDone."
        f" Converted: {success_count},"
        f" Skipped: {skipped_count},"
        f" Failed: {failed_count}"
    )
    return 0 if failed_count == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
