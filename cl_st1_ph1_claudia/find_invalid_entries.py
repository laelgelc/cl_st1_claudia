#!/usr/bin/env python3
"""
find_invalid_entries.py

This script reads a Markdown file containing a list of entries (separated by double newlines),
identifies the entries that do not contain a valid YouTube URL matching the pattern
'https://www.youtube.com/watch?v=', and exports these invalid entries into a new
Markdown file in the same directory.

The output file will have the same name as the input file, with an '_invalid_entries' suffix.

Usage:
    python find_invalid_entries.py <path_to_markdown_file>

Example:
    python find_invalid_entries.py corpus/00_sources/1000_best_pop_songs.md
"""

import sys
import os

def find_invalid_entries(input_path):
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)

    # Determine the output file name
    base_name, ext = os.path.splitext(input_path)
    output_path = f"{base_name}_invalid_entries{ext}"

    # Read the file content
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split the content into entries based on double newlines (Markdown paragraphs)
    entries = content.split('\n\n')

    invalid_entries = []

    # URL pattern to check
    valid_url_pattern = "https://www.youtube.com/watch?v="

    for entry in entries:
        # Check if it's a non-empty entry and doesn't contain the valid URL
        if entry.strip() and valid_url_pattern not in entry:
            invalid_entries.append(entry.strip())

    # Write the invalid entries to the output file
    with open(output_path, 'w', encoding='utf-8') as f:
        for invalid_entry in invalid_entries:
            f.write(invalid_entry + '\n\n')

    print(f"Process completed. Found {len(invalid_entries)} invalid entries.")
    print(f"Results saved to '{output_path}'.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python find_invalid_entries.py <path_to_markdown_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    find_invalid_entries(input_file)