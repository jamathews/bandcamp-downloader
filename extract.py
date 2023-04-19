#!/usr/bin/env python3
import argparse
import os
from glob import glob
from zipfile import ZipFile


def extract(root_dir, subfolder=None):
    archives = glob(os.path.join(os.path.abspath(root_dir), "**", "*.zip"), recursive=True)
    for archive in archives:
        with ZipFile(archive) as zipfile:
            dest = os.path.join(os.path.dirname(archive), os.path.splitext(archive)[0])
            if subfolder:
                dest = os.path.join(dest, subfolder)
            print(f"{archive}\n\t-->\t{dest}\n")
            zipfile.extractall(path=dest)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Extract your zips.')
    parser.add_argument(
        '--directory', '-d',
        default=os.getcwd(),
        help='The directory scan for zips. Defaults to the current directory.'
    )
    parser.add_argument(
        '--subfolder', '-s',
        default=None,
        help='Extraction subfolder'
    )
    args = parser.parse_args()
    extract(os.path.normcase(args.directory), args.subfolder)
