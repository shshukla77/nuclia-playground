"""Nuclia document ingestion and search."""
import asyncio
import click
from config import DATA_DIR
from indexing import upload_folder
from legacy_tests import test_semantic, test_hybrid, test_comparison, test_all
from cli import cli


@cli.command()
@click.option("--wait/--no-wait", default=True)
@click.option("--split-strategy", default="PARAGRAPH")
def upload(wait: bool, split_strategy: str):
    """Upload all documents from data folder."""
    click.echo("Uploading documents...")
    result = asyncio.run(upload_folder(DATA_DIR, wait=wait, split_strategy=split_strategy))
    click.echo("Upload complete.")
    click.echo(result)


async def test_workflow():
    """Complete workflow: upload and search."""
    print("\n" + "=" * 80)
    print("NUCLIA DOCUMENT INGESTION AND SEARCH WORKFLOW")
    print("=" * 80)
    
    print("\n1️⃣ Uploading documents...")
    await upload_folder(DATA_DIR, wait=True, split_strategy="PARAGRAPH")
    
    print("\n2️⃣ Testing searches...")
    await test_all()
    
    print("\n" + "=" * 80)
    print("✅ Workflow Complete!")
    print("=" * 80)


@cli.command(name="test")
def test_command():
    """Runs the full test workflow."""
    asyncio.run(test_workflow())

@cli.command(name="test-semantic")
def test_semantic_command():
    """Runs the semantic test."""
    asyncio.run(test_semantic())

@cli.command(name="test-hybrid")
def test_hybrid_command():
    """Runs the hybrid test."""
    asyncio.run(test_hybrid())

@cli.command(name="test-compare")
def test_comparison_command():
    """Runs the comparison test."""
    asyncio.run(test_comparison())


if __name__ == "__main__":
    cli()
