import typer
import logging
from typing import Optional
from pathlib import Path
from .downloader import download_kursliste
from opensteuerauszug.config.paths import get_xdg_data_home

app = typer.Typer(help="Manage Kursliste files.")

@app.callback()
def main():
    """
    Manage Kursliste files.
    """
    pass

@app.command()
def download(
    year: int = typer.Option(..., "--year", help="Tax year to download Kursliste for."),
    destination: Optional[Path] = typer.Option(None, "--destination", "-d", help="Directory to save the Kursliste XML file. Defaults to XDG Data Home."),
):
    """
    Downloads and prepares the Kursliste XML file for a given year.
    """
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    target_dir = destination
    if target_dir is None:
        target_dir = get_xdg_data_home() / "opensteuerauszug" / "kursliste"

    try:
        xml_path = download_kursliste(year, target_dir)
        print(f"Successfully downloaded Kursliste for {year} to {xml_path}")
    except Exception as e:
        print(f"Error downloading Kursliste: {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
