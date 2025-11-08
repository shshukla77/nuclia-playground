import click
import asyncio
from search import search_merged

@click.group()
def cli():
    pass

@cli.command()
@click.argument("question")
def ask(question):
    """Asks a question and prints the top 3 results."""
    click.echo(f"Asking: {question}")
    results = asyncio.run(search_merged(query=question, page_size=3))
    if results:
        for i, r in enumerate(results, 1):
            text = r.get("text", "N/A")[:180].strip()
            click.echo(f"{i}. {text}...")
    else:
        click.echo("No results found.")

@cli.command()
def chat():
    """Starts an interactive chat session."""
    click.echo("Starting chat session. Type 'exit' to end.")
    while True:
        question = click.prompt("Ask a question")
        if question.lower() == 'exit':
            break
        click.echo(f"You asked: {question}")
        results = asyncio.run(search_merged(query=question, page_size=3))
        if results:
            for i, r in enumerate(results, 1):
                text = r.get("text", "N/A")[:180].strip()
                click.echo(f"{i}. {text}...")
        else:
            click.echo("No results found.")

if __name__ == "__main__":
    cli()
