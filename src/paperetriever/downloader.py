import os
import requests
import csv
from .utils import get_pdf_url_from_sci_hub, prepare_folder

SCIHUB_URL = os.getenv("SCIHUB_URL", "https://sci-hub.ru")
NOT_FOUND_KEEP_PREFIX = "404."

def download_paper(identifier, output_dir, filename=None, ref_idx=None):
    prepare_folder(output_dir)

    try:
        if not filename:
            filename = identifier.replace('/', '_')

        if ref_idx is not None:
            filename = f"{ref_idx:03d}_{filename}"

        full_path = os.path.join(output_dir, filename + '.pdf')
        if os.path.exists(full_path):
            print(f"File already exists: {full_path}")
            return

        pdf_url = get_pdf_url_from_sci_hub(SCIHUB_URL, identifier)
        if not pdf_url:
            print(f"404 for {identifier}")
            with open(os.path.join(output_dir, NOT_FOUND_KEEP_PREFIX + filename + ".txt"), 'w') as f:
                f.write(identifier)
            return

        paper_response = requests.get(pdf_url)
        if paper_response.status_code == 200:
            with open(full_path, 'wb') as f:
                f.write(paper_response.content)
            print(f"Downloaded: {full_path}")
        else:
            print(f"Failed to download PDF for: {identifier}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF for: {identifier}. Error: {e}")
    except Exception as e:
        print("Some other shitty error")
        print(e)

def process_csv(csv_filename, output_dir):
    prepare_folder(output_dir)

    with open(csv_filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            title, filename = row
            download_paper(title, output_dir, filename)
