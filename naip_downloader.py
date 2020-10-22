"""
naip_downloader.py

Downloads all links in a specified csv (should have 'NIR', 'RGB', 'NIR_link', and 'RGB_link' columns) to the specified directory; unzips all .zip files in the download directory to the specified output directory.

To use, modify the csv_path, out_dir, and unzip_dir variables and then call the script from the command line.
"""

import csv
import os
import requests
import sys
import zipfile

from pathlib import Path


#: Progress bar for download
#: modified from https://sumit-ghosh.com/articles/python-download-progress-bar/
def progbar(progress, total):
    '''
    Simple output for reporting progress given current progress value and progress value at completion
    '''
    done = int(50 * progress / total)
    percent = round(100 * progress / total, 2)
    sys.stdout.write('\r[{}{}] {}%'.format('#' * done, '_' * (50 - done), percent))
    sys.stdout.flush()


#: modified from Sumit Ghosh,
#: https://sumit-ghosh.com/articles/python-download-progress-bar/
def download(url, filename):
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
        response = requests.get(url, stream=True)
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


def download_links(link_list, save_dir):
    '''
    Downloads links from link_list into save_dir. link_list is list of two-tuples: (format, link)
    '''
    d_prog = 0
    links = [l[1] for l in link_list]  #: Filter out the links from the format codes
    for link in links:
        fname = link.split('/')[-1]
        d_prog += 1
        print('Downloading {}, {} of {}'.format(fname, d_prog, str(len(links))))
        outpath = os.path.join(save_dir, fname)
        download(link, outpath)


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
    csv_path = r'c:/temp/shapefiles/ULwatershed_Final/NAIP_links_short.csv'

    out_dir = Path(r'c:/temp/shapefiles/ULwatershed_Final/downloads')
    unzip_dir = Path(r'c:/temp/shapefiles/ULwatershed_Final/unzipped')

    print('Reading CSV...')
    all_links = []
    with open(csv_path) as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            all_links.append(row)

    out_dir.mkdir(parents=True, exist_ok=True)
    unzip_dir.mkdir(parents=True, exist_ok=True)

    print(f'Downloading to {out_dir}...')
    for row in all_links:
        NIR_name = f"{row['NIR']}.zip"
        RGB_name = f"{row['RGB']}.zip"
        NIR_out = out_dir / NIR_name
        RGB_out = out_dir / RGB_name
        print(NIR_name)
        download(row['NIR_link'], NIR_out)
        print(RGB_name)
        download(row['RGB_link'], RGB_out)

    print(f'Extracting to {unzip_dir}...')
    extract_files(out_dir, unzip_dir)
