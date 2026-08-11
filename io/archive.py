

"""Find and download the best reference observation"""


from astroquery.heasarc import Heasarc
from pathlib import Path
from urllib.request import urlretrieve
from astropy.time import Time


REFERENCE_DIR = Path("data/reference")
REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

# Create a single HEASARC client
heasarc = Heasarc()


def query_archive(coords, catalog="swiftuvlog", radius="6 arcmin"):
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
        catalog=catalog,
        radius=radius,
    )


def filter_reference_candidates(table, metadata):
    """
    Remove observations that are unsuitable as reference images.
    """
    candidates = []

    for row in table:

        if row["obsid"] == metadata["obs_id"]:
            continue

        if row["filter"] != metadata["filter"]:
            continue

        if row["exposure"] <= 60:
            continue

        candidates.append(row)

    return candidates


def select_best_reference(table):
    """
    Select the longest exp
    """
    
    return max(table, key=lambda row: row["exposure"])



def download_reference_image(observation):
    """
    Download a Swift UVOT reference image.

    Parameters
    ----------
    observation : astropy.table.Row
        Row returned from the HEASARC archive.

    Returns
    -------
    pathlib.Path
        Path to the downloaded FITS image.
    """
    print("DEBUG download ref")

    # Observation ID
    obsid = str(observation["obsid"]).zfill(11)

    # Observation start time (Modified Julian Date)
    start_time = observation["start_time"]

    # Convert MJD to calendar date
    t = Time(start_time, format="mjd")
    date = t.to_datetime()

    year = date.year
    month = date.month

    # Swift archive uses YYYY_MM
    year_month = f"{year}_{month:02d}"

    filename = f"sw{obsid}uuu_sk.img.gz"

    url = (
        "https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/"
        f"{year_month}/{obsid}/uvot/image/{filename}"
    )

    output_file = REFERENCE_DIR / filename

    if not output_file.exists():
        print(f"Downloading {filename}...")
        print(f"URL: {url}")
        urlretrieve(url, output_file)

    return output_file


def find_reference_image(metadata):
    """
    Find the archival reference image w/ longest exptime
    """

    table = query_archive(metadata["skycoord"])
    print("Filters out not relevent observations.")

    filtered = filter_reference_candidates(table, metadata)
    print(f"There are {len(filtered)} swift uvot observations near the sky position of {metadata["skycoord"]} that passed the current filters.")
    best = select_best_reference(filtered)

    print("The archival image with the longest exposure time...")
    print(best)
    print("This is saved to data/reference")
    # table = filter_reference_candidates(table)

    print(best.colnames)
    return best


    # return download_reference_image(best)

def inspect_reference(observation):
    """
    Print all fields available for a reference observation.
    """

    for name in observation.colnames:
        print(f"{name}: {observation[name]}")
