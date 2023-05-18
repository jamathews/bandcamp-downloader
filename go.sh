#!/usr/bin/env bash

DOWNLOADS="bandcamp-collection"
FORMATS="mp3-320 flac"
MAPPING="artist_to_folder_mapping.json"
OUTPUT="/Volumes/music"

if [[ -z "${BANDCAMP_USERNAME}" ]]; then
    echo "Define BANDCAMP_USERNAME env var"
    exit 1
fi

for FORMAT in ${FORMATS}; do
  echo "${FORMAT}"

  pipenv run ./bandcamp-downloader.py \
    --browser firefox \
    --directory "${DOWNLOADS}/${FORMAT}" \
    --format "${FORMAT}" \
    --parallel-downloads 8 \
    --max-download-attempts 10 \
    --retry-wait 10 \
    --verbose \
    "${BANDCAMP_USERNAME}"

  pipenv run ./extract.py \
    --directory "${DOWNLOADS}/${FORMAT}" \
    --subfolder "${FORMAT}" \
    --artist_to_folder_mapping "${MAPPING}" \
    --output "${OUTPUT}"
done
