"""Validation for candidate catalogs produced by the local UVOT pipeline.

This module deliberately operates on the catalog returned by ``detect_sources``.
It does not import or depend on the legacy image-subtraction pipeline.
"""

from pathlib import Path

from astropy.table import Table


REQUIRED_COLUMNS = frozenset({"RA", "DEC", "RATE", "RATE_ERR"})


def validate_transients(catalog: Table | str | Path) -> Table:
    """Return a verified copy of a UVOT detection catalog.

    The detection step has already applied the configured source-detection
    threshold.  This validation step confirms that the catalog contains the
    coordinates and rate measurements needed by later pipeline stages, without
    relying on the legacy eight-criterion validator.

    Parameters
    ----------
    catalog
        An :class:`astropy.table.Table` returned by ``detect_sources`` or the
        path to a FITS catalog.

    Returns
    -------
    astropy.table.Table
        A copy of the verified candidate catalog.
    """

    if not isinstance(catalog, Table):
        catalog = Table.read(catalog)

    missing_columns = REQUIRED_COLUMNS.difference(catalog.colnames)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            "UVOT detection catalog is missing required column(s): "
            f"{missing}"
        )

    return catalog.copy(copy_data=True)
