from pathlib import Path
import sys

print("In main.py: import process")
from processing import process
from uvot_io.archive import get_obs_path

print("In main.py: define path")

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"

def main(obsid, filter_name):
    """
    Process a single Swift UVOT observation.
    """
    print("In main.py: set observation_path (from archive.py)")

    observation_path = get_obs_path(obsid, filter_name, DATA_DIR)    

    print(f"Processing {observation_path.name}")
    print("In main.py: run process from processing.py")

    result = process(observation_path, obsid)

    print("Done.")

    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("python main.py <obsid> <filter>")

    obsid = int(sys.argv[1])
    filter_name = sys.argv[2]
    main(obsid, filter_name)
    #example: main(30009002, "UVW1")
