#!/usr/bin/env python3
"""
fetch_youtube_metadata.py

This script reads an NDJSON file of clean YouTube URLs, fetches their metadata
using yt-dlp, and exports the enriched dataset.

The metadata captured for each video is:
- id
- url
- title
- description
- language
- uploader
- duration
- upload_date

Outputs are saved in two formats: NDJSON and TSV.

If the output NDJSON file already exists, the script skips any URLs that were
previously fetched successfully, retrying only those that failed or are new.

This revised version also supports:
- forcing a YouTube player client, defaulting to android_vr;
- retrying failed fetches;
- adding delays between requests;
- optional verbose yt-dlp debugging;
- optional yt-dlp cache removal before running.

Usage:
    python fetch_youtube_metadata.py

Optional examples:
    python fetch_youtube_metadata.py \
        --input corpus/00_sources/music_videos_list.ndjson \
        --output corpus/00_sources/music_videos.ndjson

    python fetch_youtube_metadata.py \
        --force-client android_vr \
        --retries 3 \
        --retry-delay 10 \
        --request-delay 1

    python fetch_youtube_metadata.py \
        --verbose

    python fetch_youtube_metadata.py \
        --rm-cache

Optional arguments:
    --input          Path to the input NDJSON file.
    --output         Path to the output NDJSON file. TSV uses the same base name.
    --cookies        Path to the YouTube cookies.txt file.
    --force-client   YouTube player client to force via yt-dlp extractor args.
    --retries        Number of attempts per URL.
    --retry-delay    Seconds to wait between retry attempts.
    --request-delay  Seconds to wait after each URL.
    --verbose        Enable verbose yt-dlp logging.
    --rm-cache       Remove yt-dlp cache before running.
"""

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

try:
    import yt_dlp
except ImportError:
    print(
        "Required library missing. Please install it using:\n"
        "pip install yt-dlp",
        file=sys.stderr,
    )
    sys.exit(1)


DEFAULT_YOUTUBE_CLIENT = "android_vr"
DEFAULT_RETRIES = 3
DEFAULT_RETRY_DELAY_SECONDS = 10.0
DEFAULT_REQUEST_DELAY_SECONDS = 0.0

FIELDNAMES = [
    "id",
    "url",
    "title",
    "description",
    "language",
    "uploader",
    "duration",
    "upload_date",
    "error",
]


def read_ndjson(path: Path) -> list[dict[str, Any]]:
    """Read an NDJSON file and return a list of JSON objects."""
    records = []

    with open(path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            if not line.strip():
                continue

            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON in {path} at line {line_number}: {exc}"
                ) from exc

    return records


def load_existing_successes(output_path: Path) -> dict[str, dict[str, Any]]:
    """Load successful rows from a previous output NDJSON file."""
    existing_successes = {}

    if not output_path.exists():
        return existing_successes

    with open(output_path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, 1):
            if not line.strip():
                continue

            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                print(
                    f"Warning: ignoring invalid JSON in existing output "
                    f"{output_path} at line {line_number}.",
                    file=sys.stderr,
                )
                continue

            if entry.get("url") and not entry.get("error"):
                existing_successes[entry["url"]] = entry

    return existing_successes


def build_ydl_opts(
    cookie_file: str | None,
    force_client: str | None,
    verbose: bool,
) -> dict[str, Any]:
    """Build yt-dlp Python API options."""
    ydl_opts: dict[str, Any] = {
        "quiet": not verbose,
        "verbose": verbose,
        "extract_flat": False,
        "skip_download": True,
        "noplaylist": True,
    }

    if cookie_file is not None:
        ydl_opts["cookiefile"] = cookie_file

    if force_client:
        ydl_opts["extractor_args"] = {
            "youtube": {
                "player_client": [force_client],
            }
        }

    return ydl_opts


def remove_yt_dlp_cache() -> None:
    """Remove yt-dlp cache using the CLI."""
    print("Removing yt-dlp cache...")
    result = subprocess.run(
        ["yt-dlp", "--rm-cache-dir"],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.stdout.strip():
        print(result.stdout.strip())

    if result.stderr.strip():
        print(result.stderr.strip(), file=sys.stderr)

    if result.returncode != 0:
        print(
            f"Warning: yt-dlp --rm-cache-dir exited with code {result.returncode}.",
            file=sys.stderr,
        )


def make_success_entry(url: str, info: dict[str, Any]) -> dict[str, Any]:
    """Build a successful enriched metadata entry."""
    return {
        "id": info.get("id"),
        "url": url,
        "title": info.get("title"),
        "description": info.get("description"),
        "language": info.get("language"),
        "uploader": info.get("uploader"),
        "duration": info.get("duration"),
        "upload_date": info.get("upload_date"),
    }


def make_error_entry(url: str, error: Exception | str) -> dict[str, Any]:
    """Build an enriched metadata entry for a failed fetch."""
    return {
        "id": None,
        "url": url,
        "title": None,
        "description": None,
        "language": None,
        "uploader": None,
        "duration": None,
        "upload_date": None,
        "error": str(error),
    }


def fetch_one_with_retries(
    ydl: yt_dlp.YoutubeDL,
    url: str,
    retries: int,
    retry_delay: float,
) -> dict[str, Any]:
    """Fetch metadata for one URL with retry handling."""
    last_error: Exception | None = None

    for attempt in range(1, retries + 1):
        try:
            if retries > 1:
                print(f"    Attempt {attempt}/{retries}")

            info = ydl.extract_info(url, download=False)

            if info is None:
                raise RuntimeError("yt-dlp returned no metadata.")

            return make_success_entry(url, info)

        except Exception as exc:
            last_error = exc
            print(f"    -> Attempt {attempt} failed: {exc}")

            if attempt < retries:
                print(f"    Waiting {retry_delay:g} seconds before retry...")
                time.sleep(retry_delay)

    assert last_error is not None
    return make_error_entry(url, last_error)


def write_tsv(output_path: Path, enriched_videos: list[dict[str, Any]]) -> Path:
    """Write the TSV export corresponding to the NDJSON output."""
    tsv_path = output_path.with_suffix(".tsv")

    with open(tsv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=FIELDNAMES,
            delimiter="\t",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(enriched_videos)

    return tsv_path


def fetch_youtube_metadata(
    input_path: Path,
    output_path: Path,
    cookies_path: Path,
    force_client: str | None,
    retries: int,
    retry_delay: float,
    request_delay: float,
    verbose: bool,
) -> int:
    """Fetch metadata for all URLs in an input NDJSON file."""
    if not cookies_path.exists():
        print(
            f"Warning: Cookies file not found at {cookies_path}. "
            "Requests might be limited or blocked."
        )
        cookie_file = None
    else:
        cookie_file = str(cookies_path)

    ydl_opts = build_ydl_opts(
        cookie_file=cookie_file,
        force_client=force_client,
        verbose=verbose,
    )

    input_videos = read_ndjson(input_path)
    existing_successes = load_existing_successes(output_path)
    enriched_videos = []

    print(
        f"Loaded {len(input_videos)} URLs. "
        f"Found {len(existing_successes)} previously successful fetches."
    )

    if force_client:
        print(f"Forcing YouTube player client: {force_client}")

    print("Starting metadata fetch...")

    failures = 0

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        with open(output_path, "w", encoding="utf-8") as out_f:
            for idx, entry in enumerate(input_videos, 1):
                url = entry.get("url")

                if not url:
                    print(f"[{idx}/{len(input_videos)}] Skipping entry without URL.")
                    continue

                if url in existing_successes:
                    print(
                        f"[{idx}/{len(input_videos)}] "
                        f"Skipping already successfully fetched: {url}"
                    )
                    enriched_entry = existing_successes[url]
                else:
                    print(f"[{idx}/{len(input_videos)}] Fetching metadata for: {url}")

                    enriched_entry = fetch_one_with_retries(
                        ydl=ydl,
                        url=url,
                        retries=retries,
                        retry_delay=retry_delay,
                    )

                    if enriched_entry.get("error"):
                        failures += 1
                        print(
                            f"  -> Error fetching metadata for {url}: "
                            f"{enriched_entry['error']}"
                        )
                    else:
                        print(
                            f"  -> Success: "
                            f"{enriched_entry.get('title') or enriched_entry.get('id')}"
                        )

                enriched_videos.append(enriched_entry)

                out_f.write(json.dumps(enriched_entry, ensure_ascii=False) + "\n")
                out_f.flush()

                if request_delay > 0 and idx < len(input_videos):
                    time.sleep(request_delay)

    print(f"\nNDJSON database saved to: {output_path}")

    tsv_path = write_tsv(output_path, enriched_videos)
    print(f"TSV database saved to: {tsv_path}")

    if failures:
        print(f"\nCompleted with {failures} failed metadata fetch(es).")
        return 1

    print("\nCompleted successfully.")
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch YouTube metadata for a list of URLs."
    )

    base_dir = Path(__file__).parent
    default_input = base_dir / "corpus" / "00_sources" / "music_videos_list.ndjson"
    default_output = base_dir / "corpus" / "00_sources" / "music_videos.ndjson"
    default_cookies = base_dir / "env" / "youtube_cookies.txt"

    parser.add_argument(
        "--input",
        type=Path,
        default=default_input,
        help=f"Input NDJSON file path. Default: {default_input}",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help=f"Output enriched NDJSON file path. Default: {default_output}",
    )

    parser.add_argument(
        "--cookies",
        type=Path,
        default=default_cookies,
        help=f"Path to the youtube_cookies.txt file. Default: {default_cookies}",
    )

    parser.add_argument(
        "--force-client",
        default=DEFAULT_YOUTUBE_CLIENT,
        help=(
            "YouTube player client to force via yt-dlp extractor args. "
            f"Default: {DEFAULT_YOUTUBE_CLIENT}. "
            "Use an empty string to disable forcing a client."
        ),
    )

    parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        help=f"Attempts per URL. Default: {DEFAULT_RETRIES}",
    )

    parser.add_argument(
        "--retry-delay",
        type=float,
        default=DEFAULT_RETRY_DELAY_SECONDS,
        help=f"Seconds between retry attempts. Default: {DEFAULT_RETRY_DELAY_SECONDS}",
    )

    parser.add_argument(
        "--request-delay",
        type=float,
        default=DEFAULT_REQUEST_DELAY_SECONDS,
        help=f"Seconds between URLs. Default: {DEFAULT_REQUEST_DELAY_SECONDS}",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose yt-dlp logging.",
    )

    parser.add_argument(
        "--rm-cache",
        action="store_true",
        help="Remove yt-dlp cache before fetching metadata.",
    )

    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments."""
    if not args.input.exists():
        raise FileNotFoundError(f"Input file not found at {args.input}")

    if not args.input.is_file():
        raise ValueError(f"Input path is not a file: {args.input}")

    if args.retries < 1:
        raise ValueError("--retries must be at least 1.")

    if args.retry_delay < 0:
        raise ValueError("--retry-delay must be zero or greater.")

    if args.request_delay < 0:
        raise ValueError("--request-delay must be zero or greater.")

    args.output.parent.mkdir(parents=True, exist_ok=True)


def main() -> int:
    """Programme entry point."""
    args = parse_args()

    try:
        validate_args(args)

        if args.rm_cache:
            remove_yt_dlp_cache()

        force_client = args.force_client.strip() or None

        return fetch_youtube_metadata(
            input_path=args.input,
            output_path=args.output,
            cookies_path=args.cookies,
            force_client=force_client,
            retries=args.retries,
            retry_delay=args.retry_delay,
            request_delay=args.request_delay,
            verbose=args.verbose,
        )

    except KeyboardInterrupt:
        print("\nInterrupted by user.", file=sys.stderr)
        return 130

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())