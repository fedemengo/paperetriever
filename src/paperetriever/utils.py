import os
import re
import requests
import subprocess
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

REPLACEMENTS = [
    ('/', '_sl_'), ('-', '_hy_'), (':', '_co_'), (';', '_sc_'),
    ('(', '_po_'), (')', '_pc_'), ('<', '_lt_'), ('>', '_gt_'),
    ('.', '_dt_'), ('_', '_un_'),
]

ENCODE_DICT = dict(REPLACEMENTS)
DECODE_DICT = {v: k for k, v in REPLACEMENTS}

ENCODE_PATTERN = re.compile('|'.join(map(re.escape, ENCODE_DICT.keys())))
DECODE_PATTERN = re.compile('|'.join(map(re.escape, DECODE_DICT.keys())))

def doi_to_filename(doi, ext='.json'):
    doi = re.sub(r'^(doi:|https?://doi\.org/)', '', doi, flags=re.IGNORECASE)
    encoded = ENCODE_PATTERN.sub(lambda m: ENCODE_DICT[m.group(0)], doi)
    return f"{encoded}{ext}"

def filename_to_doi(filename):
    name, ext = os.path.splitext(filename)
    if ext.lower() != '.json':
        raise ValueError("Invalid filename format: must have .json extension")
    return DECODE_PATTERN.sub(lambda m: DECODE_DICT[m.group(0)], name)

def get_doi_from_title(title):
    base_url = "https://api.crossref.org/works"
    params = {"query.title": title, "rows": 1, "sort": "score"}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['message']['items']:
            return data['message']['items'][0]['DOI']
    return None

def prepare_folder(folder_name):
    os.makedirs(folder_name, exist_ok=True)

def get_pdf_url_from_sci_hub(sci_hub_url, encoded_identifier):
    curl_command = [
        'curl', '-s', '-i', '-X', 'POST',
        '-H', 'User-Agent: curl/8.7.1',
        '-H', 'Accept: */*',
        '-H', 'Content-Type: application/x-www-form-urlencoded',
        '-d', f'request={encoded_identifier}',
        sci_hub_url
    ]

    result = subprocess.run(curl_command, capture_output=True, text=True)
    headers, _, _ = result.stdout.partition('\r\n\r\n')
    headers_dict = dict(line.split(': ', 1) for line in headers.splitlines() if ': ' in line)

    location = urljoin(sci_hub_url, headers_dict.get('location'))
    if not location:
        return None

    response = requests.get(location)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_embed = soup.find('embed', {'type': 'application/pdf'})

    if pdf_embed and 'src' in pdf_embed.attrs:
        pdf_url = pdf_embed['src']
        if pdf_url.startswith('//'):
            pdf_url = 'https:' + pdf_url
        elif not urlparse(pdf_url).scheme:
            pdf_url = 'https:' + pdf_url if pdf_url.startswith('/') else 'https://' + pdf_url

        parsed_url = urlparse(pdf_url)
        if not parsed_url.netloc:
            return None

        return pdf_url + '?download=true'

    return None
