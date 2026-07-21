#!/usr/bin/env python3
"""
describe_music.py

Describe the audible characteristics of a music recording with the Gemini API.

Usage:
    python describe_music.py song.mp3
    python describe_music.py song.mp3 --output description.txt
    python describe_music.py rap.mp3 --output rap.txt --model gemini-2.5-flash
   
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from google import genai
from google.genai import types
from google.genai.errors import APIError

SUPPORTED_FORMATS = {
    ".wav": "audio/wav",
    ".mp3": "audio/mp3",
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".ogg": "audio/ogg",
    ".m4a": "audio/m4a",
}

ANALYSIS_PROMPT = """
Listen carefully to the attached recording.

Write a continuous description of approximately 300 words describing the
recording from beginning to end.

Describe, where appropriate:

- instrumentation
- entries and exits of instruments
- vocal characteristics and processing
- tempo, rhythm, groove and meter
- dynamics
- timbre and texture
- harmony and tonal character
- production style, stereo image and effects
- mood and emotional quality
- sectional development and transitions
- salient sound events

Write continuous prose.

Base every statement exclusively on audible evidence.

Clearly distinguish confident observations from uncertain interpretations.

Do not identify or guess the song, performer, composer, album or artist.

Do not reproduce, summarize or transcribe lyrics.

Return only the description AND a label identifying the possible genres separated by a comma, eg: GENRES: a, b, c.
""".strip()


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Describe a music recording using a Gemini audio model."
    )

    parser.add_argument("audio_file", type=Path)

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output text file. Default: <audio-file>_description.txt",
    )

    parser.add_argument(
        "--model",
        default="gemini-2.5-flash",
        help="Audio-capable Gemini model.",
    )

    parser.add_argument(
        "--max-file-size-mb",
        type=float,
        default=20.0,
    )

    return parser.parse_args()


def validate_audio_file(path: Path, max_size_mb: float) -> str:
    if not path.exists():
        raise FileNotFoundError(path)

    extension = path.suffix.lower()

    if extension not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {extension}")

    size_mb = path.stat().st_size / (1024 * 1024)

    if size_mb > max_size_mb:
        raise ValueError(
            f"File is {size_mb:.1f} MB; limit is {max_size_mb:.1f} MB."
        )

    return SUPPORTED_FORMATS[extension]


def describe_music(
    client: genai.Client,
    audio_path: Path,
    mime_type: str,
    model: str,
) -> str:
    # Upload the audio file using the Gemini Files API
    uploaded_file = client.files.upload(
        file=audio_path,
        config=types.UploadFileConfig(mime_type=mime_type),
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=[uploaded_file, ANALYSIS_PROMPT],
        )
        return response.text.strip()
    finally:
        # Clean up the uploaded file from Google's servers
        client.files.delete(name=uploaded_file.name)


def main():
    args = parse_arguments()

    try:
        mime_type = validate_audio_file(
            args.audio_file,
            args.max_file_size_mb,
        )

        output = args.output or args.audio_file.with_name(
            f"{args.audio_file.stem}_description.txt"
        )

        # Force Gemini Developer API mode (Google AI Studio key)
        client = genai.Client(vertexai=False)

        print(f"Analyzing: {args.audio_file}", file=sys.stderr)
        print(f"Model: {args.model}", file=sys.stderr)

        description = describe_music(
            client,
            args.audio_file,
            mime_type,
            args.model,
        )

        output.write_text(description, encoding="utf-8")

        #print(description)
        print(f"\nSaved to: {output}", file=sys.stderr)

    except FileNotFoundError as exc:
        print(f"File error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1
    except APIError as exc:
        print(f"Gemini API error {exc.code}: {exc.message}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
