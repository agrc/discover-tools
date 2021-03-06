"""
hexagon_downloader.py

Downloads the files listed in csv_path to out_dir and unzips them to unzip_dir. csv_path should have a header and format of "url,extension". 

To use, modify the csv_path, out_dir, and unzip_dir variables and then call the script from the command line.
"""

import csv
import getpass
import os
import requests
import sys
import zipfile

from pathlib import Path


#: Progress bar for download
#: modified from https://sumit-ghosh.com/articles/python-download-progress-bar/
def progbar(progress, total, postfix=''):
    '''
    Simple output for reporting progress given current progress value and progress value at completion
    '''
    done = int(50 * progress / total)
    percent = round(100 * progress / total, 2)
    sys.stdout.write(f'\r[{"#" * done}{"_" * (50 - done)}] {percent}% {postfix}')
    sys.stdout.flush()


#: modified from Sumit Ghosh,
#: https://sumit-ghosh.com/articles/python-download-progress-bar/
def download(session, url, filename):
    '''
    Downloads url to filename using requests, reports via progress bar
    '''

    if os.path.exists(filename):
        out_dir = os.path.dirname(filename)
        out_name = os.path.basename(filename)
        name = out_name.split['.'][0]
        extension = out_name.split['.'][0]

        if name[-3:-1]:
            counter = int(name[-1])
            counter += 1
            out_name = name[:-1] + counter

        else:
            out_name = name + '_q1'

    with open(filename, 'wb') as f:
        response = session.get(url, stream=True)
        total = response.headers.get('content-length')

        if total is None:
            f.write(response.content)
        else:
            downloaded = 0
            total = int(total)
            for data in response.iter_content(chunk_size=max(int(total / 1000), 1024 * 1024)):
                downloaded += len(data)
                f.write(data)
                progbar(downloaded, total)
                sys.stdout.write('\n')


def get_file_list(directory, extensions):
    '''
    Returns a list of full filepath for all files in directory with specified extensions
    '''

    file_list = []
    for dir_name, subdir_list, files in os.walk(directory):
        for fname in files:
            if str.endswith(fname.lower(), extensions):
                file_list.append(os.path.join(dir_name, fname))

    return file_list


def extract_files(source_dir, unzip_dir):
    '''
    Extracts any .zip files from source_dir into unzip_dir. The contents of each .zip are placed in
    unzip_dir; no subfolders are created.
    '''
    z_prog = 0
    zip_list = get_file_list(source_dir, '.zip')

    for z in zip_list:
        z_prog += 1
        print('Extracting {}, {} of {}'.format(z, z_prog, str(len(zip_list))))
        with zipfile.ZipFile(z) as zip_ref:
            zip_ref.extractall(unzip_dir)


if __name__ == '__main__':
    csv_path = r'c:/temp/discover_downloads/hex_links.csv'

    out_dir = Path(r'c:/temp/discover_downloads/downloads')
    unzip_dir = Path(r'c:/temp/discover_downloads/unzipped')

    print('Reading CSV...')
    all_links = []
    with open(csv_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            all_links.append(row)

    out_dir.mkdir(parents=True, exist_ok=True)
    unzip_dir.mkdir(parents=True, exist_ok=True)

    #: We need to use a session here to preserve the login info for secured links
    print('Logging in...')
    with requests.Session() as session:
        session.post(
            'https://discover.agrc.utah.gov/login', data={
                'user': input('Username: '),
                'password': getpass.getpass()
            }
        )

        print(f'Downloading {len(all_links)} file{"s" if len(all_links) > 1 else ""} to {out_dir}...')
        tile_counter = 0

        for row in all_links:
            pieces = row['url'].split('/')
            x = pieces[-2]
            y = pieces[-1]
            z = pieces[-3]
            layer = pieces[-5]

            filename = f'{layer}_x{x}_y{y}_z{z}.{row["extension"]}'
            hex_out = out_dir / filename
            postfix = f'\t{filename}, {tile_counter+1} of {len(all_links)}'

            progbar(tile_counter, len(all_links), postfix)
            download(session, row['url'], hex_out)
            tile_counter += 1
        progbar(len(all_links), len(all_links), postfix)

    print(f'\nExtracting to {unzip_dir}...')
    extract_files(out_dir, unzip_dir)
