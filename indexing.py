from pathlib import Path
from nuclia import sdk
from utils import safe_slug_from_filename, normalize_id, wait_until_processed

try:
    from nucliadb_sdk.v2 import exceptions as ndb_exceptions
except ImportError:
    ndb_exceptions = None


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
    slug = safe_slug_from_filename(path)
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
            resource = await res_api.create(title=Path(path).name, slug=slug)
            rid = normalize_id(resource)
            is_new = True
        else:
            raise

    uploader = sdk.AsyncNucliaUpload()
    file_ext = Path(path).suffix.lower()
    mimetype = "application/pdf" if file_ext == ".pdf" else None

    upload_kwargs = {
        "path": path,
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
    """Upload all PDFs from folder in parallel."""
    import asyncio
    
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    results = {}
    pdf_files = list(data_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {data_dir}")
        return results

    # Create tasks for parallel processing
    tasks = [
        upsert_file(
            path=str(pdf_file),
            wait=wait,
            language="en",
            interpret_tables=True,
            blank_line_splitter=False,
            split_strategy=split_strategy,
        )
        for pdf_file in pdf_files
    ]
    
    # Execute all uploads in parallel
    upload_results = await asyncio.gather(*tasks)
    
    # Process results
    for pdf_file, (rid, is_new) in zip(pdf_files, upload_results):
        status = "Uploaded" if is_new else "Already indexed"
        results[pdf_file.name] = (rid, status)
        print(f"{status}: {pdf_file.name} → {rid}")

    return results
