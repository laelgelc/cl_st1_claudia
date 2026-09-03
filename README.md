# Corpus Linguistics - Study 1 - Claudia

## Phase 1 - Data Collection and Sampling

Phase 1 focuses on collecting a corpus of 1000 best pop songs, obtaining their music video audio, and preparing transcripts for linguistic analysis. The process involved data cleaning, metadata extraction, audio downloading, transcription, and descriptive statistics analysis.

### 1. Input Data Processing and Validation
The initial list of songs was provided in a Markdown document. The document was cleaned and "denoised" to normalise text and fix markdown formatting issues. During this process, several input data issues were identified and documented in the `docs/input_data_issues_report.md`:
* **Missing entries:** Songs 514 and 515 were missing from the list.
* **Duplicate entries:** Songs 372 and 961 were identified as duplicates.
* **Missing URLs:** Song 971 lacked a corresponding YouTube URL.
* **Geographical Restrictions:** 11 music videos were found to be unavailable in the researcher's region (Brazil).

### 2. URL Extraction
Using `extract_music_videos.py`, clean and unique YouTube URLs were extracted from the denoised Markdown document. The script removed accessory parameters from the URLs, filtered out duplicates, and stored the resulting list in an NDJSON file (`music_videos_list.ndjson`).

### 3. Metadata Extraction
The `fetch_youtube_metadata.py` script was used to fetch detailed metadata for each video via `yt-dlp`.
The collected metadata includes the video ID, URL, title, description, language, uploader, duration, and upload date. The enriched dataset was saved to `music_videos.ndjson` and a TSV equivalent, providing a structured catalog of the music videos.

### 4. Audio Downloading
To prepare the dataset for transcription, `download_music_videos_audio.py` was used to download the audio tracks. The script relies on `yt-dlp` to directly download the audio in a format optimized for Whisper (WAV, mono, 16kHz, s16le PCM). It deduplicated records, verified availability, and organized the output into a structured directory with accompanying metadata, descriptions, and subtitles.

### 5. Transcription
The downloaded audio files were transcribed using **WhisperX** via `transcribe_music_videos_whisperx.py`. This provided automated, high-quality speech-to-text transcripts for each music video, saving the outputs in the transcripts folder.

### 6. Descriptive Statistics Analysis
Data processing and analysis were carried out using the Jupyter Notebook `cl_st1_ph1_claudia.ipynb`. The notebook performed the following steps:
* Loaded the `music_videos.ndjson` dataset.
* Calculated the word count for each generated transcript.
* Evaluated video availability and removed the raw error logs from the dataset.
* Conducted descriptive statistics on the `transcript_word_count`, plotting a boxplot and identifying the Interquartile Range (IQR) and non-outlier bounds.
* Tagged videos that fall within the IQR and non-outlier range.
* Exported the final curated dataset as NDJSON, TSV, and XLSX files (`music_videos_dataset`).

### 7. Audio Content Description
Additionally, `describe_music.py` was introduced to interface with the Gemini API. This tool allows for describing the audible characteristics of a music recording (instrumentation, tempo, dynamics, mood, etc.) to enrich the dataset with qualitative descriptions based purely on audio evidence.
