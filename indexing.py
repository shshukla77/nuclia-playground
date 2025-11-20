from pathlib import Path
from nuclia import sdk
from utils import safe_slug_from_filename, normalize_id, wait_until_processed
from config import DATA_DIR
import logging

logger = logging.getLogger(__name__)

try:
    from nucliadb_sdk.v2 import exceptions as ndb_exceptions
except ImportError:
    ndb_exceptions = None


def validate_file_path(path: str) -> Path:
    """
    Validate that file path is within DATA_DIR to prevent path traversal.
    
    Args:
        path: File path to validate
        
    Returns:
        Resolved Path object
        
    Raises:
        ValueError: If path is outside DATA_DIR or doesn't exist
    """
    file_path = Path(path).resolve()
    data_dir_resolved = DATA_DIR.resolve()
    
    # Check if path is within DATA_DIR
    try:
        file_path.relative_to(data_dir_resolved)
    except ValueError:
        raise ValueError(f"File path must be within {data_dir_resolved}")
    
    if not file_path.exists():
        raise ValueError(f"File does not exist: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    return file_path


async def upsert_file(
    path: str,
    wait: bool = False,
    extract_strategy: str | None = None,
    split_strategy: str | None = None,
    language: str = "en",
    interpret_tables: bool = True,
    blank_line_splitter: bool = False,
) -> tuple[str, bool]:
    """Upload or update file in Nuclia KB with change detection."""
    # Validate file path before processing
    validated_path = validate_file_path(path)
    path_str = str(validated_path)
    
    slug = safe_slug_from_filename(path_str)
    current_hash = slug
    res_api = sdk.AsyncNucliaResource()
    is_new = False

    try:
        res = await res_api.get(slug=slug, show=["basic", "extra"])
        rid = normalize_id(res)

        extra_obj = getattr(res, "extra", None)
        extra_dict = (
            extra_obj.model_dump()
            if hasattr(extra_obj, "model_dump")
            else (extra_obj.dict() if hasattr(extra_obj, "dict") else {})
        )
        prev_hash = ((extra_dict or {}).get("metadata", {}) or {}).get("ingest_hash")

        if prev_hash == current_hash:
            return rid, False

    except Exception as e:
        if (ndb_exceptions and isinstance(e, ndb_exceptions.NotFoundError)) or "Resource does not exist" in str(e):
            resource = await res_api.create(title=Path(path_str).name, slug=slug)
            rid = normalize_id(resource)
            is_new = True
        else:
            raise

    uploader = sdk.AsyncNucliaUpload()
    file_ext = Path(path_str).suffix.lower()
    mimetype = "application/pdf" if file_ext == ".pdf" else None

    upload_kwargs = {
        "path": path_str,
        "rid": rid,
        "extra": {"metadata": {"language": language}},
        "interpretTables": interpret_tables,
        "blanklineSplitter": blank_line_splitter,
    }

    if mimetype:
        upload_kwargs["mimetype"] = mimetype
    if extract_strategy:
        upload_kwargs["extract_strategy"] = extract_strategy
    if split_strategy:
        upload_kwargs["split_strategy"] = split_strategy

    await uploader.file(**upload_kwargs)
    await res_api.update(rid=rid, extra={"metadata": {"ingest_hash": current_hash}})

    if wait:
        await wait_until_processed(rid)

    return rid, is_new


async def upload_folder(
    data_dir: Path,
    wait: bool = False,
    split_strategy: str = "PARAGRAPH",
) -> dict[str, tuple[str, str]]:
    """Upload all PDFs from folder."""
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    results = {}
    pdf_files = list(data_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {data_dir}")
        return results

    for pdf_file in pdf_files:
        rid, is_new = await upsert_file(
            path=str(pdf_file),
            wait=wait,
            language="en",
            interpret_tables=True,
            blank_line_splitter=False,
            split_strategy=split_strategy,
        )
        status = "Uploaded" if is_new else "Already indexed"
        results[pdf_file.name] = (rid, status)
        print(f"{status}: {pdf_file.name} → {rid}")

    return results
