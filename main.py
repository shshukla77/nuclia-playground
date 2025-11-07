"""Nuclia document ingestion and search."""
import asyncio
import sys
from config import DATA_DIR
from indexing import upload_folder
from search import search_semantic, search_hybrid, search_merged
from tests import test_semantic, test_hybrid, test_comparison, test_all


async def upload_data_folder(wait: bool = False, split_strategy: str = "PARAGRAPH") -> dict:
    """Upload all documents from data folder."""
    return await upload_folder(DATA_DIR, wait=wait, split_strategy=split_strategy)


async def test_workflow():
    """Complete workflow: upload and search."""
    print("\n" + "=" * 80)
    print("NUCLIA DOCUMENT INGESTION AND SEARCH WORKFLOW")
    print("=" * 80)
    
    print("\n1️⃣ Uploading documents...")
    await upload_data_folder(wait=True, split_strategy="PARAGRAPH")
    
    print("\n2️⃣ Testing searches...")
    await test_all()
    
    print("\n" + "=" * 80)
    print("✅ Workflow Complete!")
    print("=" * 80)


def main():
    """Entry point."""
    asyncio.run(upload_data_folder(wait=True, split_strategy="PARAGRAPH"))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "test":
            asyncio.run(test_workflow())
        elif mode == "semantic":
            asyncio.run(test_semantic())
        elif mode == "hybrid":
            asyncio.run(test_hybrid())
        elif mode == "compare":
            asyncio.run(test_comparison())
        else:
            print("Usage: python main.py [test|semantic|hybrid|compare]")
    else:
        main()
