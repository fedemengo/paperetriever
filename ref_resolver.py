#!/usr/bin/env python

import os
import sys
import requests
import json
import base64

from scihub_dl import download_paper

REF_DIR = "./refs/"

def doi_to_filename(doi):
    # Use base64 encoding to ensure reversibility
    encoded_doi = base64.urlsafe_b64encode(doi.encode()).decode()
    return f"{encoded_doi}.json"

def filename_to_doi(filename):
    # Remove the .json extension and decode the base64
    encoded_doi = filename.rsplit('.', 1)[0]
    return base64.urlsafe_b64decode(encoded_doi).decode()

def get_doi_from_title(title):
    base_url = "https://api.crossref.org/works"
    params = {
        "query.title": title,
        "rows": 1,
        "sort": "score",
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data['message']['items']:
            return data['message']['items'][0]['DOI']
        else:
            print(f"No DOI found for the article: {title}")
            return None
    else:
        print(f"Error: Unable to search for DOI. Status code: {response.status_code}")
        return None

def parse_unstructured_ref(unstructured_ref):
    parts = unstructured_ref.split('.')
    author = parts[0].strip()
    title = None
    if len(parts) > 1:
        title = parts[1].split('\n')[0].strip()
    return author, title

def get_references_from_doi(doi):
    base_url = f"https://api.crossref.org/works/{doi}"
    print(base_url)

    response = requests.get(base_url)

    if response.status_code == 200:
        data = response.json()

        if 'reference' in data['message']:
            references = data['message']['reference']

            ref_list = []
            for ref in references:
                ref_info = {}
                if 'DOI' in ref:
                    ref_info['DOI'] = ref['DOI']
                if 'unstructured' in ref:
                    author, title = parse_unstructured_ref(ref['unstructured'])
                    ref_info['authors'] = author
                    ref_info['title'] = title
                if 'year' in ref:
                    ref_info['year'] = ref['year']

                if ref_info:
                    ref_list.append(ref_info)

            return ref_list
        else:
            print("No references found for this DOI.")
            return []
    else:
        print(f"Error: Unable to retrieve data. Status code: {response.status_code}")
        return []

def get_references_from_title(title):
    doi = get_doi_from_title(title)
    if doi:
        print(f"Found DOI: {doi}")
        filename = doi_to_filename(doi)
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                data = json.load(file)
        return data, doi

        references = get_references_from_doi(doi)

        with open(filename, 'w') as f:
            json.dump(references, f, indent=2)
        print(f"References saved to {filename}")

        return references, doi
    else:
        return [], None

def get_first_author(authors_str):
    return authors_str.split(' ')[0].strip()

def retrieve_paper(ref):
    doi = ref.get('DOI')
    title = ref.get('title')
    year = ref.get('year')
    fauthor = get_first_author(ref.get('authors'))

    search_term = doi
    if doi is None:
        search_term = title

    filename = f"{fauthor}_{year}"
    if len(fauthor) < 2 or year is None:
        filename = title

    if len(filename) < 5:
        print("Not enough information to create file", ref)
        return

    try:
        download_paper(search_term, REF_DIR, filename + ".pdf")
    except:
        print(ref)


# Example usage
article_title = sys.argv[1]
references, doi = get_references_from_title(article_title)

if doi:
    os.makedirs(REF_DIR, exist_ok=True)
    filename = doi_to_filename(doi)
    recovered_doi = filename_to_doi(filename)

    print(f"References for article '{article_title}' (DOI: {doi}):")
    for i, ref in enumerate(references, 1):
        print(f"{i}. DOI: {ref.get('DOI', 'N/A')}, Author: {ref.get('author', 'N/A')}, Title: {ref.get('title', 'N/A')}")
        retrieve_paper(ref)

    # Demonstrate reversibility
    print(f"\nOriginal DOI: {doi}")
    print(f"Filename: {filename}")
    print(f"Recovered DOI: {recovered_doi}")
    print(f"Reversible: {doi == recovered_doi}")
else:
    print("No references found.")
