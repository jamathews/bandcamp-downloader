#!/usr/bin/env bash

# Load environment variables from .env
if [ ! -f .env ]; then
  echo "Error: .env file not found. See .env.example for an example."
  exit 1
fi
set -o allexport
source .env
set +o allexport

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
if [[ -f "${SCRIPT_DIR}/.env" ]]; then
  source "${SCRIPT_DIR}/.env"
fi

if [[ -z "${BANDCAMP_USERNAME}" ]]; then
    echo "Define BANDCAMP_USERNAME env var"
    exit 1
fi

cd "${SCRIPT_DIR}" && pipenv sync

for FORMAT in ${FORMATS}; do
  echo "${FORMAT}"

  pipenv run ./bandcamp-downloader.py \
    --browser firefox \
    --directory "${DOWNLOADS}/${FORMAT}" \
    --format "${FORMAT}" \
    --parallel-downloads 8 \
    --max-download-attempts 10 \
    --retry-wait 10 \
    --wait-after-download 10 \
    "${BANDCAMP_USERNAME}"

  pipenv run ./extract.py \
    --directory "${DOWNLOADS}/${FORMAT}" \
    --subfolder "${FORMAT}" \
    --artist_to_folder_mapping "${MAPPING}" \
    --output "${OUTPUT}"
done
