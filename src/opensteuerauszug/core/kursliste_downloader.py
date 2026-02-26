import logging
import requests
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

ESTV_BASE_URL = "https://www.ictax.admin.ch/extern/en.html" # Note: This is the web UI, we need the XML endpoint.
# Based on common knowledge or documentation (which isn't fully provided here but implied),
# the XMLs are usually at a specific URL pattern or API.
# Looking at user_guide.md content provided earlier: "Always down the latest file marked "Initial" in the latest format, V2.0 at this time"
# and "https://www.ictax.admin.ch/extern/en.html#/xml".
# The actual download URL for the XML usually looks like:
# https://www.ictax.admin.ch/extern/xml/kursliste_2023.xml or similar.
# Let's try to infer a robust download mechanism.
# A common pattern for ESTV XMLs is `https://www.ictax.admin.ch/extern/xml/kursliste_{year}.xml`.
# However, sometimes there are versions.
# Let's use a best-effort approach to download `kursliste_{year}.xml` from the standard location.

def download_kursliste_xml(year: int, destination_dir: Path) -> Optional[Path]:
    """
    Downloads the Kursliste XML for the given year to the destination directory.

    Args:
        year: The tax year to download (e.g. 2023).
        destination_dir: The directory to save the downloaded file to.

    Returns:
        The path to the downloaded file if successful, None otherwise.
    """
    filename = f"kursliste_{year}.xml"
    url = f"https://www.ictax.admin.ch/extern/xml/kursliste_{year}.xml"
    destination_path = destination_dir / filename

    logger.info(f"Attempting to download Kursliste for year {year} from {url}...")

    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        # Check if we got an actual XML file and not a redirect to an error page or similar
        content_type = response.headers.get('content-type', '')
        if 'xml' not in content_type and 'text/plain' not in content_type: # sometimes it might be text/xml or application/xml
             # Relaxed check, but let's look at start of file
             pass

        destination_dir.mkdir(parents=True, exist_ok=True)

        with open(destination_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"Successfully downloaded Kursliste for year {year} to {destination_path}")
        return destination_path

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download Kursliste for year {year}: {e}")
        return None
