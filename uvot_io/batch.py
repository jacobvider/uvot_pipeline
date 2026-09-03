"""Read a UVOT batch manifest and locate its FITS input images."""

from __future__ import annotations

from dataclasses import dataclass
import filecmp
from pathlib import Path, PurePosixPath
import shutil
from zipfile import ZipFile


@dataclass(frozen=True)
class ManifestEntry:
    """One ``filename|version|EXTNAME`` record from ``to_process.log``."""

    filename: str
    version: str
    extension_name: str
    line_number: int

    @property
    def input_filename(self) -> str:
        """Name to use after extraction.

        The supplied ZIP members have a ``.gz`` suffix but are plain FITS
        streams (their first bytes are ``SIMPLE``).  Removing the suffix keeps
        Astropy from treating the extracted files as gzip-compressed.
        """

        return self.filename.removesuffix(".gz")

    @property
    def output_key(self) -> str:
        """A collision-free directory name for this image extension."""

        source_name = self.input_filename.removesuffix(".img")
        return f"{source_name}_v{self.version}_{self.extension_name}"


@dataclass(frozen=True)
class ZipMember:
    """The ZIP file and member that contain a manifest input image."""

    archive_path: Path
    member_name: str
    file_size: int


@dataclass(frozen=True)
class LocalInput:
    """A locally available FITS image supplied through ``--source-dir``."""

    source_path: Path
    file_size: int


def parse_manifest(path: str | Path) -> list[ManifestEntry]:
    """Parse a ``filename|version|EXTNAME`` batch manifest.

    The middle field is a Swift image version, not an HDU number.  The last
    field is the FITS ``EXTNAME`` and is what identifies the image extension.
    """

    manifest_path = Path(path)
    if not manifest_path.is_file():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    entries: list[ManifestEntry] = []
    errors: list[str] = []
    for line_number, raw_line in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line:
            continue

        fields = [field.strip() for field in line.split("|")]
        if len(fields) != 3 or not all(fields):
            errors.append(
                f"line {line_number}: expected filename|version|EXTNAME"
            )
            continue

        filename, version, extension_name = fields
        if PurePosixPath(filename).name != filename or not filename.endswith(
            ".img.gz"
        ):
            errors.append(
                f"line {line_number}: invalid input filename {filename!r}"
            )
            continue

        entries.append(
            ManifestEntry(filename, version, extension_name, line_number)
        )

    if errors:
        raise ValueError("Invalid manifest:\n" + "\n".join(errors))
    if not entries:
        raise ValueError(f"Manifest has no entries: {manifest_path}")
    return entries


def index_archives(archive_paths: list[str | Path]) -> dict[str, ZipMember]:
    """Return image ZIP members indexed by their FITS filename.

    Only normal input-image members are considered; archived development files
    under ``Python_Code_OLD`` are intentionally excluded.
    """

    members: dict[str, ZipMember] = {}
    for raw_archive_path in archive_paths:
        archive_path = Path(raw_archive_path)
        if not archive_path.is_file():
            raise FileNotFoundError(f"ZIP archive not found: {archive_path}")

        with ZipFile(archive_path) as archive:
            for info in archive.infolist():
                posix_path = PurePosixPath(info.filename)
                if (
                    info.is_dir()
                    or "Python_Code_OLD" in posix_path.parts
                    or not posix_path.name.endswith(".img.gz")
                ):
                    continue

                filename = posix_path.name
                member = ZipMember(archive_path, info.filename, info.file_size)
                previous = members.get(filename)
                if previous and previous != member:
                    raise ValueError(
                        f"Input image {filename} occurs in both "
                        f"{previous.archive_path} and {archive_path}"
                    )
                members[filename] = member

    return members


def index_source_directories(
    source_directories: list[str | Path],
) -> dict[str, LocalInput]:
    """Return FITS files from local directories, indexed by filename.

    Directories are searched recursively so a downloaded Google Drive folder
    can be supplied unchanged.  A filename may occur only once across all
    source directories, which prevents the batch from choosing an arbitrary
    input when duplicate files are present.
    """

    inputs: dict[str, LocalInput] = {}
    for raw_directory in source_directories:
        directory = Path(raw_directory)
        if not directory.is_dir():
            raise NotADirectoryError(f"Input directory not found: {directory}")

        for source_path in directory.rglob("*.img.gz"):
            if not source_path.is_file():
                continue
            filename = source_path.name
            input_file = LocalInput(source_path, source_path.stat().st_size)
            previous = inputs.get(filename)
            if previous and previous.source_path != source_path:
                if not filecmp.cmp(
                    previous.source_path, source_path, shallow=False
                ):
                    raise ValueError(
                        f"Input image {filename} occurs in both "
                        f"{previous.source_path.parent} and {source_path.parent} "
                        "with different contents"
                    )
                continue
            inputs[filename] = input_file

    return inputs


def index_inputs(
    archive_paths: list[str | Path], source_directories: list[str | Path]
) -> dict[str, ZipMember | LocalInput]:
    """Combine image members from ZIP archives and local source directories."""

    inputs: dict[str, ZipMember | LocalInput] = {}
    for input_index in (
        index_archives(archive_paths),
        index_source_directories(source_directories),
    ):
        for filename, input_file in input_index.items():
            if filename in inputs:
                raise ValueError(
                    f"Input image {filename} was supplied more than once; "
                    "use either --archive or --source-dir for that file."
                )
            inputs[filename] = input_file

    if not inputs:
        raise ValueError("Supply at least one --archive ZIP or --source-dir")
    return inputs


def missing_filenames(
    entries: list[ManifestEntry], members: dict[str, ZipMember | LocalInput]
) -> list[str]:
    """Return the unique manifest filenames absent from the supplied ZIPs."""

    return sorted({entry.filename for entry in entries if entry.filename not in members})


def extract_input(
    member: ZipMember | LocalInput, destination: str | Path
) -> Path:
    """Stage one ZIP member or local FITS input atomically.

    The staged filename omits ``.gz`` because the supplied files are plain
    FITS streams despite their suffix.  This prevents Astropy from attempting
    gzip decompression when the image is later opened.
    """

    destination_path = Path(destination)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    if destination_path.is_file() and destination_path.stat().st_size == member.file_size:
        return destination_path

    temporary_path = destination_path.with_name(destination_path.name + ".part")
    if isinstance(member, ZipMember):
        with ZipFile(member.archive_path) as archive:
            with archive.open(member.member_name) as source:
                with temporary_path.open("wb") as target:
                    shutil.copyfileobj(source, target, length=1024 * 1024)
    else:
        with member.source_path.open("rb") as source:
            with temporary_path.open("wb") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)
    temporary_path.replace(destination_path)
    return destination_path
