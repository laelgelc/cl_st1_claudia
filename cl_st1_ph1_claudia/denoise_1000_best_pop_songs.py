#!/usr/bin/env python3
import unicodedata
import os

def denoise_markdown(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Normalize unicode to convert math alphanumerics to standard ASCII and strip zero-width noise
    text = unicodedata.normalize('NFKC', text)

    # Clean up Pandoc's underline artifact
    text = text.replace('{.underline}', '')

    # Clean up the double brackets artifact from the links
    text = text.replace('[[', '[').replace(']]', ']')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    print(f"Denoised document saved to '{output_path}'.")

if __name__ == "__main__":
    input_file = "corpus/00_sources/1000_best_pop_songs.md"
    output_file = "corpus/00_sources/1000_best_pop_songs_denoised.md"
    denoise_markdown(input_file, output_file)