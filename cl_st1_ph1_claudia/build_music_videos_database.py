"""
build_music_videos_database.py

This script reads a DOCX file containing a list of music videos, extracts metadata
(rank, artist, song, year, description) and embedded hyperlinks (YouTube URLs),
and exports the dataset into an NDJSON (Newline Delimited JSON) file.

Usage:
    python build_music_videos_database.py

Optional arguments:
    --input  Path to the input DOCX file.
    --output Path to the output NDJSON file.
"""

import argparse
import json
import re
from pathlib import Path

try:
    import docx
except ImportError:
    raise ImportError("The 'python-docx' library is required. Please install it using: pip install python-docx")


def extract_hyperlink_from_paragraph(paragraph):
    """
    Extracts the first hyperlink found in a python-docx paragraph.
    Requires parsing the underlying XML because python-docx does not expose
    hyperlinks directly in its high-level API.
    """
    for run in paragraph._p.xpath(".//w:hyperlink"):
        r_id = run.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        if r_id in paragraph.part.rels:
            return paragraph.part.rels[r_id].target_ref
    return None


def parse_docx_to_ndjson(input_path: Path, output_path: Path):
    doc = docx.Document(input_path)

    # Regex pattern to match: "1000- Imagine Dragons, Believer - 2017 - Description text"
    # Group 1: Rank, Group 2: Artist, Group 3: Song, Group 4: Year, Group 5: Description
    pattern = re.compile(r"^(\d+)\s*-\s*(.*?),\s*(.*?)\s*-\s*(\d{4})\s*-\s*(.*)")

    music_videos = []

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        match = pattern.match(text)
        if match:
            url = extract_hyperlink_from_paragraph(paragraph)

            entry = {
                "rank": int(match.group(1)),
                "artist": match.group(2).strip(),
                "song": match.group(3).strip(),
                "year": match.group(4).strip(),
                "description": match.group(5).strip(),
                "url": url
            }
            music_videos.append(entry)

    # Write to NDJSON
    with open(output_path, 'w', encoding='utf-8') as f:
        for mv in music_videos:
            f.write(json.dumps(mv, ensure_ascii=False) + '\n')

    print(f"Successfully extracted {len(music_videos)} music videos.")
    print(f"Database saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Build a music video database from a DOCX file.")

    default_input = Path(__file__).parent / "corpus" / "00_sources" / "1000_best_pop_songs.docx"
    default_output = Path(__file__).parent / "corpus" / "00_sources" / "music_videos.ndjson"

    parser.add_argument(
        "--input",
        type=Path,
        default=default_input,
        help=f"Input DOCX file path. Default: {default_input}"
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

    parse_docx_to_ndjson(args.input, args.output)


if __name__ == "__main__":
    main()