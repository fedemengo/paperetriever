import os
import json
import requests
from .utils import doi_to_filename, get_doi_from_title

def parse_unstructured_ref(unstructured_ref):
    parts = unstructured_ref.split('.')
    author = parts[0].strip()
    title = parts[1].split('\n')[0].strip() if len(parts) > 1 else None
    return author, title

def get_references_from_doi(doi):
    base_url = f"https://api.crossref.org/works/{doi}"
    response = requests.get(base_url)

    if response.status_code != 200:
        return []

    data = response.json()
    if 'reference' not in data['message']:
        return []

    references = data['message']['reference']
    ref_list = []

    for i, ref in enumerate(references, 1):
        ref_info = {
            'ref_idx': i,
            'DOI': ref.get('DOI'),
            'year': ref.get('year')
        }

        if 'unstructured' in ref:
            author, title = parse_unstructured_ref(ref['unstructured'])
            ref_info['authors'] = author
            ref_info['title'] = title

        if any(ref_info.values()):
            ref_list.append(ref_info)

    return ref_list

def get_references_from_title(title, output_dir):
    doi = get_doi_from_title(title)
    if not doi:
        return [], None

    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, doi_to_filename(doi))

    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return json.load(file), doi

    references = get_references_from_doi(doi)

    with open(filename, 'w') as f:
        json.dump(references, f, indent=2)

    return references, doi

def get_first_author(authors_str):
    return authors_str.split(' ')[0].strip()
