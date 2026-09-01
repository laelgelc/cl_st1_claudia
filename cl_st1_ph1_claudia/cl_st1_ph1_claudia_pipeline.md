# Corpus Linguistics - Study 1 - Phase 1 - Claudia

Run the commands from the project phase directory, e.g.:

```text
cl_st1_ph1_claudia/
```

## 1. Extract the music videos list

```shell script
python extract_music_videos.py
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

```shell script
python download_music_video_audio.py
```