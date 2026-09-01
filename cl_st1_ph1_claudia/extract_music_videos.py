"""
extract_music_videos.py

This script reads a Markdown file containing a list of music videos, extracts
unique hyperlinks (YouTube URLs) that match the 'https://www.youtube.com/watch?v=' pattern,
logs any duplicated URLs, and exports the unique URLs into an NDJSON (Newline Delimited JSON) file
under the 'url' key.

Usage:
    python extract_music_videos.py

Optional arguments:
    --input  Path to the input Markdown file.
    --output Path to the output NDJSON file.
"""

import argparse
import json
import re
from pathlib import Path


def parse_md_to_ndjson(input_path: Path, output_path: Path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    music_videos = []
    seen_urls = set()
    duplicates_count = 0

    # Regex pattern to match the YouTube URLs and ignore trailing Markdown syntax like ')', ']', etc.
    url_pattern = re.compile(r"https://www\.youtube\.com/watch\?v=[^\s\)\]\"]+")

    for match in url_pattern.finditer(content):
        url = match.group(0)
        if url not in seen_urls:
            seen_urls.add(url)
            entry = {
                "url": url
            }
            music_videos.append(entry)
        else:
            print(f"Duplicate URL found and skipped: {url}")
            duplicates_count += 1

    # Write to NDJSON
    with open(output_path, 'w', encoding='utf-8') as f:
        for mv in music_videos:
            f.write(json.dumps(mv, ensure_ascii=False) + '\n')

    print(f"Successfully extracted {len(music_videos)} unique music videos.")
    if duplicates_count > 0:
        print(f"Total duplicates skipped: {duplicates_count}")
    print(f"Database saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Build a music video database from a Markdown file.")

    default_input = Path(__file__).parent / "corpus" / "00_sources" / "1000_best_pop_songs.md"
    default_output = Path(__file__).parent / "corpus" / "00_sources" / "music_videos_list.ndjson"

    parser.add_argument(
        "--input",
        type=Path,
        default=default_input,
        help=f"Input Markdown file path. Default: {default_input}"
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=default_output,
        help=f"Output NDJSON file path. Default: {default_output}"
    )

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: Input file not found at {args.input}")
        return

    parse_md_to_ndjson(args.input, args.output)


if __name__ == "__main__":
    main()