import re
import os
from pathlib import Path
from nuclia import sdk
from nucliadb_models.metadata import ResourceProcessingStatus

try:
    from nucliadb_sdk.v2 import exceptions as ndb_exceptions
except ImportError:
    ndb_exceptions = None


def safe_slug_from_filename(path: str) -> str:
    """Generate slug from filename + mtime for idempotency."""
    filename = Path(path).stem
    safe_name = re.sub(r"[^A-Za-z0-9_\-:]", "_", filename)
    return f"{safe_name}-{int(os.path.getmtime(path))}"


def normalize_id(resource_or_id):
    """Extract resource ID as string from SDK response or string."""
    if isinstance(resource_or_id, str):
        return resource_or_id
    rid = getattr(resource_or_id, "id", None)
    if isinstance(rid, str) and rid:
        return rid
    raise RuntimeError("Could not normalize resource id from SDK response")


async def wait_until_processed(rid: str, interval: int = 2, timeout: int = 900):
    """Poll resource until PROCESSED status with exponential backoff."""
    res_api = sdk.AsyncNucliaResource()
    import asyncio
    deadline = asyncio.get_event_loop().time() + timeout
    current_interval = interval
    max_interval = 30
    backoff_multiplier = 1.5
    
    while True:
        res = await res_api.get(rid=rid, show=["basic"])
        if res.metadata.status == ResourceProcessingStatus.PROCESSED:
            return res
        if asyncio.get_event_loop().time() > deadline:
            raise TimeoutError(f"Timed out waiting for {rid}")
        
        await asyncio.sleep(current_interval)
        # Exponential backoff: increase interval up to max
        current_interval = min(current_interval * backoff_multiplier, max_interval)
