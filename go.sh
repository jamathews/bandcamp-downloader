#!/usr/bin/env bash

DOWNLOADS="bandcamp-collection"
#FORMAT="mp3-320"
FORMAT="flac"
MAPPING="artist_to_folder_mapping.json"
OUTPUT="~/Desktop/test_music"

if [[ -z "${BANDCAMP_USERNAME}" ]]; then
    echo "Define BANDCAMP_USERNAME env var"
    exit 1
fi

pipenv run ./bandcamp-downloader.py \
  --browser firefox \
  --directory "${DOWNLOADS}" \
  --format "${FORMAT}" \
  --parallel-downloads 8 \
  --max-download-attempts 10 \
  --retry-wait 10 \
  --verbose \
  "${BANDCAMP_USERNAME}"

pipenv run ./extract.py \
  --directory "${DOWNLOADS}" \
  --subfolder "${FORMAT}" \
  --artist_to_folder_mapping "${MAPPING}" \
  --output "${OUTPUT}"

echo "Review the contents in ${OUTPUT}. If it looks right, run:
rsync --archive --human-readable --progress --one-file-system --verbose ${OUTPUT}/ /Volumes/music"
