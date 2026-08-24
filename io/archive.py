"""Find and download the best reference observation"""

from astroquery.heasarc import Heasarc
from pathlib import Path
from urllib.request import urlretrieve
from astropy.time import Time

REFERENCE_DIR = Path("data/reference")
REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

# Create a single HEASARC client
heasarc = Heasarc()

def query_archive(coords, mission="swiftuvlog", radius="6 arcmin"):
    """
    Query the HEASARC Swift UVOT archive around a sky position.

    Parameters
    ----------
    coords : astropy.coordinates.SkyCoord
        Sky position of the observation.
    mission : str
        HEASARC mission table to query.
    radius : str
        Search radius.

    Returns
    -------
    astropy.table.Table
        Table of nearby Swift observations.
    """

    return heasarc.query_region(
        position=coords,
        mission=mission,
        radius=radius,
    )


def filter_reference_candidates(table, metadata):
    """
    Remove observations that are unsuitable as reference images.
    """
    print("In archive.py: filter_reference_candidates")

    candidates = []

    print("Target obsid:", metadata["obs_id"])
    print("Target filter:", metadata["filter"])
    for row in table[:10]:
        print(
            row["OBSID"],
            row["FILTER"],
            row["EXPOSURE"],
        )

    print("Available filters:")
    print(set(table["FILTER"]))

    for row in table:

        if row["OBSID"] == metadata["obs_id"]:
            continue

        if row["FILTER"].strip() != metadata["filter"].strip():
            continue

        if row["EXPOSURE"] <= 60:
            continue

        candidates.append(row)

    return candidates


def select_best_reference(table):
    """
    Select the longest exp
    """
    
    return max(table, key=lambda row: row["EXPOSURE"])


def download_reference_image(observation, metadata):
    print(">>> download_reference_image() called")
    breakpoint()
    """
    Download the selected Swift UVOT reference image.

    Parameters
    ----------
    observation : astropy.table.Row
        Selected reference observation.
    metadata : dict
        Metadata for the target observation.

    Returns
    -------
    pathlib.Path
        Path to the downloaded image.
    """
    print("In archive.py: download_reference_image")

    obsid = str(observation["OBSID"]).zfill(11)

    # Observation date
    t = Time(observation["START_TIME"], format="mjd")
    date = t.to_datetime()
    year_month = f"{date.year}_{date.month:02d}"

    # Convert HEASARC filter name to filename code
    filter_map = {
        "U": "uuu",
        "UVW1": "uw1",
        "UVM2": "um2",
        "UVW2": "uw2",
        "B": "ubb",
        "V": "uvv",
        "WHITE": "uwh",
    }

    filter_name = observation["FILTER"].strip().upper()

    if filter_name not in filter_map:
        raise ValueError(f"Unsupported filter: {filter_name}")

    filter_code = filter_map[filter_name]

    # filename = f"sw{obsid}{filter_code}_sk.img.gz"
    filename = f"sw{obsid}uw1_sk.img.gz"
    print(filename)


    url = (
        "https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/"
        f"{year_month}/{obsid}/uvot/image/{filename}"
    )

    output_file = REFERENCE_DIR / filename

    if not output_file.exists():
        print(f"Downloading {filename}")
        print(f"URL: {url}")
        urlretrieve(url, output_file)

    return output_file

print("In archive.py: find_reference_image")

def find_reference_image(metadata):
    """
    Find the archival reference image w/ longest exptime
    """

    table = query_archive(metadata["skycoord"])

    # Debug: inspect the returned table
    print("Columns:")
    print(table.colnames)
    print()

    print("First few rows:")
    print(table[:5])
    print()

    print("Filters out not relevent observations.")

    filtered = filter_reference_candidates(table, metadata)
    print(f'There are {len(filtered)} swift uvot observations near the sky position of {metadata["skycoord"]} that passed the current filters.')

    best = select_best_reference(filtered)
    print(best["FILTER"])

    print("The archival image with the longest exposure time...")
    print(best)

    return download_reference_image(best, metadata)

    # return download_reference_image(best)

def inspect_reference(observation):
    """
    Print all fields available for a reference observation.
    """

    for name in observation.colnames:
        print(f"{name}: {observation[name]}")
