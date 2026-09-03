"""Find, select, and download Swift UVOT reference observations."""

from pathlib import Path
from urllib.request import urlretrieve

from astroquery.heasarc import Heasarc
from astropy.table import Table
from astropy.time import Time


REFERENCE_DIR = Path("data/reference")
MAX_TARGETS = 15
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
    """Return the number of rows in a catalog, or ``None`` if it is absent."""

    if isinstance(catalog, (str, Path)):
        catalog_path = Path(catalog)
        if not catalog_path.is_file():
            return None
        catalog = Table.read(catalog_path)
    return len(catalog)


def has_acceptable_target_count(
    catalog: Table | str | Path, maximum: int = MAX_TARGETS
) -> bool:
    """Return whether a catalog has at most ``maximum`` detected sources."""

    if maximum < 0:
        raise ValueError("maximum must be non-negative")
    target_count = count_targets(catalog)
    return target_count is None or target_count <= maximum


def _normalized_obsid(obsid) -> str:
    """Return a canonical eleven-digit Swift observation ID."""

    return str(obsid).strip().zfill(11)


def query_archive(coords, mission: str = "swiftuvlog", radius: str = "6 arcmin"):
    """Query HEASARC for Swift UVOT observations near *coords*."""

    return heasarc.query_region(position=coords, mission=mission, radius=radius)


def filter_reference_candidates(table, metadata):
    """Keep different, same-filter observations with exposure longer than 60 s."""

    candidates = []
    for row in table:
        if _normalized_obsid(row["OBSID"]) == _normalized_obsid(metadata["obs_id"]):
            continue
        if str(row["FILTER"]).strip() != str(metadata["filter"]).strip():
            continue
        if row["EXPOSURE"] <= 60:
            continue
        candidates.append(row)
    return candidates


def select_best_reference(candidates):
    """Select the candidate with the longest exposure."""

    if not candidates:
        raise LookupError("No suitable archival reference observations found")
    return max(candidates, key=lambda row: row["EXPOSURE"])


def find_reference_image(metadata):
    """Find the best same-filter archival reference for an input image."""

    return select_best_reference(
        filter_reference_candidates(query_archive(metadata["skycoord"]), metadata)
    )


def image_filename(obsid, filter_name) -> str:
    """Return the standard Swift UVOT sky-image filename."""

    filter_name = str(filter_name).strip().upper()
    if filter_name not in FILTER_MAP:
        raise ValueError(f"Unsupported filter: {filter_name}")
    return f"sw{_normalized_obsid(obsid)}{FILTER_MAP[filter_name]}_sk.img.gz"


def get_obs_path(obsid, filter_name, directory: str | Path) -> Path:
    """Return a local archive observation, downloading it if needed."""

    directory = Path(directory)
    observation_path = directory / image_filename(obsid, filter_name)
    if not observation_path.is_file():
        observation_path = download_image(obsid, filter_name, directory)
    return observation_path


def _lookup_start_time(obsid: str):
    """Get an observation's start time for legacy single-image downloads."""

    table = heasarc.query_region(
        position="0 0",
        mission="swiftuvlog",
        radius="361 deg",
        obsid=obsid,
        fields="All",
        resultmax=1,
    )
    if len(table) == 0:
        raise ValueError(f"ObsID {obsid} not found")
    return table[0]["START_TIME"]


def download_image(
    obsid,
    filter_name,
    directory: str | Path = REFERENCE_DIR,
    *,
    start_time=None,
) -> Path:
    """Download one UVOT sky image if it does not already exist locally."""

    normalized_obsid = _normalized_obsid(obsid)
    if start_time is None:
        start_time = _lookup_start_time(normalized_obsid)

    date = Time(start_time, format="mjd").to_datetime()
    year_month = f"{date.year}_{date.month:02d}"
    filename = image_filename(normalized_obsid, filter_name)
    url = (
        "https://heasarc.gsfc.nasa.gov/FTP/swift/data/obs/"
        f"{year_month}/{normalized_obsid}/uvot/image/{filename}"
    )

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    output_file = directory / filename
    if not output_file.exists():
        print(f"Downloading {filename}")
        urlretrieve(url, output_file)
    return output_file


def download_observation(metadata):
    """Download the input observation described by its metadata."""

    return download_image(metadata["obs_id"], metadata["filter"])


def download_reference_image(observation, directory: str | Path | None = None) -> Path:
    """Download a selected reference without repeating an archive lookup."""

    return download_image(
        observation["OBSID"],
        observation["FILTER"],
        directory=REFERENCE_DIR if directory is None else directory,
        start_time=observation["START_TIME"],
    )


def inspect_reference(observation):
    """Print all fields available for a reference observation."""

    for name in observation.colnames:
        print(f"{name}: {observation[name]}")
