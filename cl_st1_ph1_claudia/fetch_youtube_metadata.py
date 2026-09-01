"""
fetch_youtube_metadata.py

This script reads an NDJSON file of clean YouTube URLs, fetches their metadata using yt-dlp
and a provided cookies file, and exports the enriched dataset.

The metadata captured for each video (in order) is:
- id
- url
- title
- description
- language
- uploader
- duration
- upload_date

Outputs are saved in two formats: NDJSON and TSV.
If the output NDJSON file already exists, the script will skip any URLs that
were previously fetched successfully, retrying only those that failed or are new.

Usage:
    python fetch_youtube_metadata.py

Optional arguments:
    --input   Path to the input NDJSON file.
    --output  Path to the output NDJSON file (TSV will use the same base name).
    --cookies Path to the YouTube cookies.txt file.
"""

import argparse
import csv
import json
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Required library missing. Please install it using:\npip install yt-dlp", file=sys.stderr)
    sys.exit(1)


def fetch_youtube_metadata(input_path: Path, output_path: Path, cookies_path: Path):
    if not cookies_path.exists():
        print(f"Warning: Cookies file not found at {cookies_path}. Requests might be limited or blocked.")
        cookie_file = None
    else:
        cookie_file = str(cookies_path)

    # Configure yt-dlp to just extract metadata without downloading
    ydl_opts = {
        'quiet': True,
        'extract_flat': False,  # False extracts full metadata like description, duration, etc.
        'skip_download': True,
        'cookiefile': cookie_file
    }

    input_videos = []
    enriched_videos = []
    existing_successes = {}

    # Read the input NDJSON list
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                input_videos.append(json.loads(line))

    # Read existing output if available to cache successes (for retry logic)
    if output_path.exists():
        with open(output_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    # If there's no error, we consider it a successful fetch
                    if entry.get("url") and not entry.get("error"):
                        existing_successes[entry["url"]] = entry

    print(f"Loaded {len(input_videos)} URLs. Found {len(existing_successes)} previously successful fetches.")
    print("Starting metadata fetch...")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        with open(output_path, 'w', encoding='utf-8') as out_f:
            for idx, entry in enumerate(input_videos, 1):
                url = entry.get("url")
                if not url:
                    continue

                # Check if we already have successful data for this URL
                if url in existing_successes:
                    print(f"[{idx}/{len(input_videos)}] Skipping already successfully fetched: {url}")
                    enriched_entry = existing_successes[url]
                else:
                    print(f"[{idx}/{len(input_videos)}] Fetching metadata for: {url}")
                    try:
                        # Extract video info
                        info = ydl.extract_info(url, download=False)

                        # Create enriched entry in the specific requested order
                        enriched_entry = {
                            "id": info.get("id"),
                            "url": url,
                            "title": info.get("title"),
                            "description": info.get("description"),
                            "language": info.get("language"),
                            "uploader": info.get("uploader"),
                            "duration": info.get("duration"),
                            "upload_date": info.get("upload_date")
                        }

                    except Exception as e:
                        print(f"  -> Error fetching metadata for {url}: {e}")
                        # Keep the structure even if it fails, recording the error
                        enriched_entry = {
                            "id": None,
                            "url": url,
                            "title": None,
                            "description": None,
                            "language": None,
                            "uploader": None,
                            "duration": None,
                            "upload_date": None,
                            "error": str(e)
                        }

                enriched_videos.append(enriched_entry)

                # Write enriched entry progressively to NDJSON
                out_f.write(json.dumps(enriched_entry, ensure_ascii=False) + '\n')

    print(f"\nNDJSON database saved to: {output_path}")

    # Generate TSV Export
    tsv_path = output_path.with_suffix('.tsv')
    with open(tsv_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ["id", "url", "title", "description", "language", "uploader", "duration", "upload_date", "error"]
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(enriched_videos)
    print(f"TSV database saved to: {tsv_path}")


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube metadata for a list of URLs.")

    base_dir = Path(__file__).parent
    default_input = base_dir / "corpus" / "00_sources" / "music_videos_list.ndjson"
    default_output = base_dir / "corpus" / "00_sources" / "music_videos.ndjson"
    default_cookies = base_dir / "env" / "youtube_cookies.txt"

    parser.add_argument(
        "--input",
        type=Path,
        default=default_input,
        help=f"Input NDJSON file path. Default: {default_input}"
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help=f"Output enriched NDJSON file path. Default: {default_output}"
    )

    parser.add_argument(
        "--cookies",
        type=Path,
        default=default_cookies,
        help=f"Path to the youtube_cookies.txt file. Default: {default_cookies}"
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found at {args.input}", file=sys.stderr)
        return

    fetch_youtube_metadata(args.input, args.output, args.cookies)


if __name__ == "__main__":
    main()