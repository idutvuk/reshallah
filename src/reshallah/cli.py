from typing_extensions import Annotated
import asyncio

import typer

from .typst_compiler import compile_simple_typst
from .mcp_server import run_mcp_server


def main(
        directory: Annotated[str, typer.Option("--dir", "-d")],
        output: Annotated[str, typer.Option("--output", "-o")] = "output",
):
    """CLI for compile directories with typst"""
    outfile_name = compile_simple_typst(directory, output)
    typer.echo(f"compiled, output at {outfile_name}")


app = typer.Typer()


@app.command()
def compile(
        directory: Annotated[str, typer.Option("--dir", "-d")],
        output: Annotated[str, typer.Option("--output", "-o")] = "output",
):
    """Compile a Typst document directory to PDF"""
    main(directory, output)


@app.command()
def mcp():
    """Run as MCP server"""
    asyncio.run(run_mcp_server())

def cli_main():
    app()

if __name__ == "__main__":
    cli_main()
