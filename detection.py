#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Jacob Vider, jacobisaacvider@gmail.com
Date:   Wed Aug 26 2026
"""
"""Source detection for UVOT difference images."""

from pathlib import Path

from astropy.table import Table
import heasoftpy as hsp


def detect_sources(
    difference_image: str | Path,
    *,
    output_dir: str | Path,
    threshold: float,
) -> tuple[Table | None, Path]:
    """Run HEASoft ``uvotdetect`` on the first image HDU of a summed image."""

    difference_image = Path(difference_image)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    catalog_path = output_dir / "uvotDetect.fits"
    region_path = output_dir / "uvotDetect.reg"

    task = hsp.HSPTask("uvotdetect")
    result = task(
        infile=f"{difference_image}+1",
        outfile=str(catalog_path),
        expfile="NONE",
        threshold=threshold,
        sexfile="DEFAULT",
        plotsrc="yes",
        expopt="ALPHA",
        calibrate="no",
        regfile=str(region_path),
        clobber="yes",
        cleanup="yes",
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    if not catalog_path.is_file():
        return None, region_path
    return Table.read(catalog_path), region_path
