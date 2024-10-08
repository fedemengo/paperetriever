#!/usr/bin/env python

import sys
import csv
import subprocess
import requests
import os
import glob
import urllib.parse
from bs4 import BeautifulSoup

SCIHUB_URL = "https://sci-hub.ru"
NOT_FOUND_KEEP_PREFIX = "404."

def download_paper(title, folder, filename):
    full_path = os.path.join(folder, filename)
    if os.path.exists(full_path):
        print(f"file already exists: {full_path}")
        return

    encoded_title = title
    try:
        encoded_title = urllib.parse.quote_plus(title)
    except:
        print(f"cannot parse {title}")
        print("exiting")
        raise ValueError(f"cannot parse {title}")

    # curl since raw python doesnt seem to be working
    curl_command = [
        'curl', '-s', '-i', '-X', 'POST',
        '-H', 'User-Agent: curl/8.7.1',
        '-H', 'Accept: */*',
        '-H', 'Content-Type: application/x-www-form-urlencoded',
        '-d', f'request={encoded_title}',
        SCIHUB_URL
    ]

    try:
        result = subprocess.run(curl_command, capture_output=True, text=True)
        headers, _, _ = result.stdout.partition('\r\n\r\n')
        headers_dict = dict(line.split(': ', 1) for line in headers.splitlines() if ': ' in line)

        location = headers_dict.get('location')
        if location:
            print(f"get pdf embedding page from url={location}")
            response = requests.get(location)
            soup = BeautifulSoup(response.text, 'html.parser')
            pdf_embed = soup.find('embed', {'type': 'application/pdf'})

            if pdf_embed and 'src' in pdf_embed.attrs:
                pdf_url = pdf_embed['src']
                if pdf_url.startswith('//'):
                    pdf_url = 'https:' + pdf_url
                pdf_url += '?download=true'

                print(f"downloading from url={pdf_url}")
                paper_response = requests.get(pdf_url)
                if paper_response.status_code == 200:
                    with open(full_path, 'wb') as f:
                        f.write(paper_response.content)
                    print(f"downloaded: {full_path}")
                else:
                    raise ValueError(f"failed to download PDF for: {title}")
            else:
                raise ValueError(f"no PDF link found for: {title}")
        else:
            raise ValueError(f"no Location header found for: {title}")
    except:  # noqa
        print("404 for", title)
        with open(os.path.join(folder, NOT_FOUND_KEEP_PREFIX + filename + ".txt"), 'w') as f:
            f.write(title)
            f.close()


def prepare_folder(folder_name):
    os.makedirs(folder_name, exist_ok=True)
    for filename in glob.glob(os.path.join(folder_name, NOT_FOUND_KEEP_PREFIX + "*")):
        os.remove(filename)

def process_csv(csv_filename):
    folder_name = os.path.splitext(csv_filename)[0]
    prepare_folder(folder_name)

    with open(csv_filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            title, filename = row
            download_paper(title, folder_name, filename)

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py csv_file1.csv csv_file2.csv ...")
        sys.exit(1)

    for csv_filename in sys.argv[1:]:
        if not os.path.exists(csv_filename):
            print(f"file not found: {csv_filename}")
            continue
        print(f"processing {csv_filename}...")
        process_csv(csv_filename)


if __name__ == "__main__":
    main()
