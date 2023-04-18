#!/usr/bin/env bash

DOWNLOADS="bandcamp-collection"

if [[ -z "${BANDCAMP_USERNAME}" ]]; then
    echo "Define BANDCAMP_USERNAME env var"
    exit 1
fi

pipenv run ./bandcamp-downloader.py \
  --browser firefox \
  --directory "${DOWNLOADS}" \
  --format flac \
  --parallel-downloads 8 \
  --max-download-attempts 10 \
  --retry-wait 10 \
  --verbose \
  "${BANDCAMP_USERNAME}"

pipenv run ./extract.py \
  --directory "${DOWNLOADS}"