"""Find and download the best reference observation"""

from astroquery.heasarc import Heasarc
from pathlib import Path
from urllib.request import urlretrieve
from astropy.time import Time
from astropy.table import Table


REFERENCE_DIR = Path("data/reference")
REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

MAX_TARGETS = 15

# Create a single HEASARC client
heasarc = Heasarc()
FILTER_MAP = {
    "U": "uuu",
    "UVW1": "uw1",
    "UVM2": "um2",
    "UVW2": "uw2",
    "B": "ubb",
    "V": "uvv",
    "WHITE": "uwh",
}


def count_targets(catalog: Table | str | Path) -> int | None:
    """Return the number of targets in a detection catalog.

    A missing catalog means the observation has not been processed yet, so
    ``None`` is returned rather than treating it as a rejected observation.
    """

    if isinstance(catalog, (str, Path)):
        catalog_path = Path(catalog)
        if not catalog_path.is_file():
            return None
        catalog = Table.read(catalog_path)

    return len(catalog)


def has_acceptable_target_count(catalog: Table | str | Path,
maximum: int = MAX_TARGETS,
) -> bool:
    """Return whether a catalog has at most ``maximum`` detected targets."""

    if maximum < 0:
        raise ValueError("maximum must be non-negative")

    target_count = count_targets(catalog)
    return target_count is None or target_count <= maximum

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


###apply quality filters

def filter_reference_candidates(table, metadata):
    """
    Remove observations that are unsuitable as reference images.
    """
    print("In archive.py: filter_reference_candidates")

    candidates = []

    print("In archive.py: Target obsid:", metadata["obs_id"])
    print("In archive.py: Target filter:", metadata["filter"])
    for row in table[:10]:
        print(
            row["OBSID"],
            row["FILTER"],
            row["EXPOSURE"],
        )

    print("In archive.py: Available filters:")
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

print("In archive.py: find_reference_image")
def find_reference_image(metadata):
    """
    Find the archival reference image w/ longest exptime
    """

    table = query_archive(metadata["skycoord"])

    # Debug: inspect the returned table
    print("In archive.py, in find_reference_image: print reference image")
    print("In archive.py: Columns:")
    print(table.colnames)
    print()

    print("In archive.py: First few rows:")
    print(table[:5])
    print()

    print("In archive.py, in find_reference_image: filters out not relevent observations.")

    filtered = filter_reference_candidates(table, metadata)
    print(f'In archive.py, in find_reference_image: There are {len(filtered)} swift uvot observations near the sky position of {metadata["skycoord"]} that passed the current filters.')
    print('In archive.py, in find_reference_image: [filtered] data')
    print(f'In archive.py {filtered}')

    best = select_best_reference(filtered)

    print(best["FILTER"])

    print("In archive.py, in find_reference_image: The archival image with the longest exposure time...")
    print(best)
    return best

    # return download_reference_image(best, metadata)
    # return download_reference_image(best)

def image_filename(obsid, filter_name):
    """
    Return the standard Swift UVOT image filename.
    """

    filter_name = filter_name.strip().upper()

    if filter_name not in FILTER_MAP:
        raise ValueError(f"Unsupported filter: {filter_name}")

    obsid = str(obsid).zfill(11)
    filter_code = FILTER_MAP[filter_name]

    return f"sw{obsid}{filter_code}_sk.img.gz"

def get_obs_path(obsid, filter_name, directory):
    """
    Return the local path to an observation.
    Download it first if it is not already present.
    """

    observation_path = directory / image_filename(obsid, filter_name)

    if not observation_path.exists():
        observation_path = download_image(
            obsid,
            filter_name,
            directory,
        )

    return observation_path

def download_image(obsid, filter_name, directory=REFERENCE_DIR):
    """
    Download a Swift UVOT image given its ObsID and filter.

    Parameters
    ----------
    obsid : str
        Swift observation ID.
    filter_name : str
        UVOT filter name (e.g. "U", "UVW1").
    directory : pathlib.Path
        Directory where the image should be saved.

    Returns
    -------
    pathlib.Path
        Path to the downloaded image.
    """


    normalized_obsid = str(obsid).zfill(11)
    table = heasarc.query_region(
        position="0 0",
        mission="swiftuvlog",
        radius="361 deg", ##fix this
        obsid=normalized_obsid,
        fields="All",
        resultmax=1,
    )

#ONE OTHER THING:  
# the object querying step should remove the observation itself from the list.  
# this is important in case we are running things either in real time but "late", or if we're testing on old observations

#QUERY_RADIUS = "9.4 arcmin" # set as global varaible
# ##### heasarc.query_region(
#                 coords,
#                 catalog="swiftuvlog",
#                 radius=QUERY_RADIUS,
#                 columns=(
#                     "OBSID,RA,DEC,START_TIME,EXPOSURE,"
#                     "ASP_CORR,FILTER,FILENAME,EXTNAME"
#                 ) )

### add code from pipeline


    if len(table) == 0:
        raise ValueError(f"ObsID {obsid} not found.")

    start_time = table[0]["START_TIME"]

    t = Time(start_time, format="mjd")
    date = t.to_datetime()
    year_month = f"{date.year}_{date.month:02d}"

    filename = image_filename(obsid, filter_name)

    obsid = normalized_obsid

    url = (
        "https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/"
        f"{year_month}/{obsid}/uvot/image/{filename}"
    )

    directory.mkdir(parents=True, exist_ok=True)
    output_file = directory / filename
    #00014012162_uu791523077I


    if not output_file.exists():
        print(f"Downloading {filename}")
        print(f"URL: {url}")
        urlretrieve(url, output_file)

    return output_file

def download_observation(metadata):
    """
    Download the input observation described by metadata.
    """
    return download_image(
        metadata["obs_id"],
        metadata["filter"],
    )


def download_reference_image(observation):
    """
    Download the selected archival reference image.
    """
    return download_image(
        observation["OBSID"],
        observation["FILTER"],
    )

# def download_reference_image(observation, metadata):
#     print(">>> download_reference_image() called")
#     breakpoint()
#     """
#     Download the selected Swift UVOT reference image.

#     Parameters
#     ----------
#     observation : astropy.table.Row
#         Selected reference observation.
#     metadata : dict
#         Metadata for the target observation.

#     Returns
#     -------
#     pathlib.Path
#         Path to the downloaded image.
#     """
#     print("In archive.py: download_reference_image")

#     obsid = str(observation["OBSID"]).zfill(11)

#     # Observation date
#     t = Time(observation["START_TIME"], format="mjd")
#     date = t.to_datetime()
#     year_month = f"{date.year}_{date.month:02d}"

#     # Convert HEASARC filter name to filename code
#     filter_map = {
#         "U": "uuu",
#         "UVW1": "uw1",
#         "UVM2": "um2",
#         "UVW2": "uw2",
#         "B": "ubb",
#         "V": "uvv",
#         "WHITE": "uwh",
#     }

#     filter_name = observation["FILTER"].strip().upper()

#     if filter_name not in filter_map:
#         raise ValueError(f"Unsupported filter: {filter_name}")

#     filter_code = filter_map[filter_name]

#     #filename = f"sw{obsid}{filter_code}_sk.img.gz"
#     filename = f"sw{obsid}uw1_sk.img.gz"
#     print(filename)


#     url = (
#         "https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/"
#         f"{year_month}/{obsid}/uvot/image/{filename}"
#     )

#     output_file = REFERENCE_DIR / filename

#     if not output_file.exists():
#         print(f"Downloading {filename}")
#         print(f"URL: {url}")
#         urlretrieve(url, output_file)

#     return output_file


def inspect_reference(observation):
    """
    Print all fields available for a reference observation.
    """

    for name in observation.colnames:
        print(f"{name}: {observation[name]}")
