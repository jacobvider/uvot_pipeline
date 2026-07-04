from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

LOG_DIR = PROCESSED_DIR / "logs"

POINTING_TOLERANCE_ARCSEC = 2.0