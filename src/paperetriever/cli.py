import click
from .downloader import download_paper, process_csv
from .resolver import get_references_from_title, get_doi_from_title

@click.group()
def cli():
    """Reference Manager CLI for retrieving and managing academic references."""
    pass

@cli.command()
@click.argument('identifier')
@click.option('--output-dir', '-o', default='./papers', help='Output directory for downloaded papers')
def download(identifier, output_dir):
    """Download a paper given a title or DOI."""
    doi = get_doi_from_title(identifier) if '/' not in identifier else identifier
    if doi:
        download_paper(doi, output_dir)
    else:
        click.echo(f"Could not find DOI for: {identifier}")

@cli.command()
@click.argument('identifier')
@click.option('--output-dir', '-o', default='./refs', help='Output directory for downloaded references')
@click.option('--download-refs', '-d', is_flag=True, help='Download reference papers')
def resolve_references(identifier, output_dir, download_refs):
    """Resolve references from a given title or DOI and optionally download them."""
    references, doi = get_references_from_title(identifier, output_dir)
    if references:
        click.echo(f"Found {len(references)} references for DOI: {doi}")
        for ref in references:
            click.echo(f"- {ref.get('title', 'No title')} ({ref.get('DOI', 'No DOI')})")
            if download_refs:
                download_paper(ref.get('DOI') or ref.get('title'), output_dir, ref_idx=ref['ref_idx'])
    else:
        click.echo(f"No references found for: {identifier}")

@cli.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='./papers', help='Output directory for downloaded papers')
def process_csv_command(csv_file, output_dir):
    """Process a CSV file and download the references to the file system."""
    process_csv(csv_file, output_dir)


if __name__ == '__main__':
    cli()
