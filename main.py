#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jacob Vider, jacobisaacvider@gmail.com
Date:   Wed Aug 26 2026
"""
from pathlib import Path
import sys

print("In main.py: import process")
from processing import process
from uvot_io.archive import get_obs_path, image_filename

print("In main.py: define path")
DATA_DIR = Path(
    "/mnt/c/Users/jacob/research/spring_2026/"
    "image_subtraction_pipeline_to_process"
)


def main(obsid, filter_name):
    """
    Process a single Swift UVOT observation.
    """
    print("In main.py: set observation_path")

    observation_path = DATA_DIR / image_filename(obsid, filter_name)

    print("In main.py: check if observation_path exists")

    if not observation_path.exists():
        observation_path = get_obs_path(obsid, filter_name, DATA_DIR)    
        print(observation_path)

    print(f"Processing {observation_path.name}")
    print("In main.py: run process from processing.py")

    result = process(observation_path)

    print("Done.")

    return result


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("python main.py <obsid> <filter>")

    obsid = int(sys.argv[1])
    filter_name = sys.argv[2]
    main(obsid, filter_name)
    #example: main(30009002, "UVW1")
