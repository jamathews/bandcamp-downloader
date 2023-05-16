#!/usr/bin/env python3
import argparse
import json
import os
from glob import glob
from pathlib import Path
from shutil import move
from zipfile import ZipFile


class Mapper:
    def __init__(self, mapping_file, output_dir):
        self._mapping = None
        self._mapping_file = mapping_file
        self._output_dir = output_dir

    @property
    def mapping(self):
        if not self._mapping:
            self._load()
        return self._mapping

    def _load(self):
        if os.path.isfile(self._mapping_file):
            with open(self._mapping_file) as mapping_file:
                self._mapping = json.load(mapping_file)
        if not self._mapping:
            self._mapping = dict()
            self._save()

    def _save(self):
        with open(self._mapping_file, "w") as mapping_file:
            json.dump(self._mapping, mapping_file, indent=4, sort_keys=True)

    def add(self, artist, folder):
        self.mapping[artist] = str(folder)
        self._save()

    def get_artist_root_folder(self, artist):
        folder = self.mapping.get(artist)
        if folder:
            return folder
        else:
            folder = self._get_folder(artist)
            self.add(artist, folder)
            return self.get_artist_root_folder(artist)

    def _get_folder(self, artist):
        if self._output_dir and os.path.isdir(self._output_dir):
            existing = glob(os.path.join(self._output_dir, "*", artist))
            if existing and len(existing) == 1 and os.path.basename(existing[0]) == artist:
                existing_target_folder = os.path.dirname(existing[0])
                return os.path.basename(existing_target_folder)
        prompt = f"What folder should {artist} go into?"
        folder = Path(input(prompt))
        return folder


def extract(zip_dir, output_dir, subfolder=None, artist_mapper=None):
    extract_zips(artist_mapper, output_dir, subfolder, zip_dir)
    move_non_archives(artist_mapper, output_dir, zip_dir)


def move_non_archives(artist_mapper, output_dir, zip_dir):
    non_archives = glob(os.path.join(os.path.abspath(zip_dir), "**", "*.mp3"), recursive=True)
    non_archives += glob(os.path.join(os.path.abspath(zip_dir), "**", "*.flac"), recursive=True)
    for non_archive in non_archives:
        dest = get_dest(non_archive, artist_mapper, output_dir, None)
        dest = os.path.dirname(dest)
        dest = os.path.join(dest, os.path.basename(non_archive))
        if os.path.isfile(dest):
            print(f'Destination Exists: "{dest}"')
        else:
            print(f'"{non_archive}"\n\t-->\t"{dest}"\n')
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            move(src=non_archive, dst=dest)


def extract_zips(artist_mapper, output_dir, subfolder, zip_dir):
    archives = glob(os.path.join(os.path.abspath(zip_dir), "**", "*.zip"), recursive=True)
    for archive in archives:
        with ZipFile(archive) as zipfile:
            dest = get_dest(archive, artist_mapper, output_dir, subfolder)
            if os.path.exists(dest):
                print(f'Destination Exists: "{dest}"')
            else:
                print(f'"{archive}"\n\t-->\t"{dest}"\n')
                zipfile.extractall(path=dest)


def get_dest(archive, artist_mapper, output_dir, subfolder):
    artist = os.path.split(os.path.dirname(archive))[-1]
    dest = os.path.join(output_dir,
                        artist_mapper.get_artist_root_folder(artist),
                        artist,
                        os.path.splitext(os.path.basename(archive))[0]
                        )
    if subfolder:
        dest = os.path.join(dest, subfolder)
    return dest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract your zips.')
    parser.add_argument(
        '--directory', '-d',
        default=os.getcwd(),
        help='The directory scan for zips. Defaults to the current directory.'
    )
    parser.add_argument(
        '--output', '-o',
        default=None,
        help='Extraction root'
    )
    parser.add_argument(
        '--subfolder', '-s',
        default=None,
        help='Extraction subfolder'
    )
    parser.add_argument(
        '--artist_to_folder_mapping', '-f',
        default=None,
        help='Artist to folder mapping'
    )
    args = parser.parse_args()
    if not args.artist_to_folder_mapping:
        print("Provide a mapping file with --artist_to_folder_mapping <filename>")
        exit(-1)

    zips = os.path.abspath(os.path.expandvars(os.path.expanduser(args.directory)))
    output = os.path.abspath(os.path.expandvars(os.path.expanduser(args.output)))
    mapping = os.path.abspath(os.path.expandvars(os.path.expanduser(args.artist_to_folder_mapping)))
    mapper = Mapper(mapping, output)

    extract(zip_dir=zips, output_dir=output, subfolder=args.subfolder, artist_mapper=mapper)
