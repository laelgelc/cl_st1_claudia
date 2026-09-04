# Corpus Linguistics - Study 1 - Phase 1 - Claudia

Run the commands from the project phase directory, e.g.:

```text
cl_st1_ph1_claudia/
```

## 0. Find invalid entries in the input Markdown document

```shell script
python find_invalid_entries.py \
    corpus/00_sources/1000_best_pop_songs_denoised.md
```

Output: `corpus/00_sources/1000_best_pop_songs_denoised_invalid_entries.md`


## 1. Extract the music videos list

```shell script
python extract_music_videos.py \
    --input corpus/00_sources/1000_best_pop_songs_denoised.md \
    --output corpus/00_sources/music_videos_list.ndjson
```

Output: `corpus/00_sources/music_videos_list.ndjson`


## 2. Enrich the music videos list with YouTube metadata

```shell script
python fetch_youtube_metadata.py
```

Outputs:

- `corpus/00_sources/music_videos.ndjson`
- `corpus/00_sources/music_videos.tsv`
- `corpus/00_sources/music_videos.xlsx`

## 3. Download music video audio

### Test mode

```shell script
python download_music_videos_audio.py \
    --cookies env/youtube_cookies.txt
```

### Production mode on an EC2 instance

```shell script
bash run_python_ec2.sh \
    download_music_videos_audio.py \
    --no-test-mode \
    --cookies env/youtube_cookies.txt
```

## 4. Transcribe music video audio with WhisperX

WhisperX failed to transcribe a few music video audio files.

### Default test run

```shell script
python transcribe_music_videos_whisperx.py
```

### Explicit one-item test run

```shell script
python transcribe_music_videos_whisperx.py --test-limit 1
```

### Full run

```shell script
python transcribe_music_videos_whisperx.py --no-test-mode
```

## 4. Transcribe music video audio with Gemini

### Test runs

```shell script
python transcribe_music_videos_gemini.py \
    --start-corpus-id aUzBgeI5dpc
```

```shell script
python transcribe_music_videos_gemini.py \
    --start-corpus-id IePTH1PWzAs
```

```shell script
python transcribe_music_videos_gemini.py \
    --start-corpus-id gOMhN-hfMtY
```

```shell script
python transcribe_music_videos_gemini.py \
    --start-corpus-id mcCK99wHrk0
```

### Full run

```shell script
python transcribe_music_videos_gemini.py --no-test-mode
```

### Production mode on an EC2 instance

```shell script
bash run_python_ec2.sh \
    transcribe_music_videos_gemini.py \
    --no-test-mode
```

Two audio files, `Q0iqg2UanEc` and `sDo-GA1hLk4`, repeatedly returned empty model responses with `gemini-3.6-flash`, despite the audio files being valid and listenable. These two items were reprocessed successfully with `gemini-3.5-flash`.

```shell script
python transcribe_music_videos_gemini.py \
    --model-name gemini-3.5-flash \
    --start-corpus-id Q0iqg2UanEc
```

```shell script
python transcribe_music_videos_gemini.py \
    --model-name gemini-3.5-flash \
    --start-corpus-id sDo-GA1hLk4
```

## 5. Describe music video music with Gemini

### Default test run

```shell script
python describe_music_videos_music.py
```

### Explicit one-item test run

```shell script
python describe_music_videos_music.py --test-limit 1
```

### Full run

```shell script
python describe_music_videos_music.py --no-test-mode
```

### Production mode on an EC2 instance

```shell script
bash run_python_ec2.sh \
    describe_music_videos_music.py \
    --no-test-mode
```
