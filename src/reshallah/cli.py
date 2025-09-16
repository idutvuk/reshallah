from typing_extensions import Annotated
import asyncio

import typer

from .typst_compiler import compile_simple_typst
from .mcp_server import run_mcp_server

app = typer.Typer()

# cli tools have not been tested, may not work
@app.command()
def main(
        directory: Annotated[str, typer.Option("--dir", "-d")],
        output: Annotated[str, typer.Option("--output", "-o")] = "output",
):
    outfile_name = compile_simple_typst(directory, output)
    typer.echo(f"compiled, output at {outfile_name}")


@app.command()
def mcp():
    asyncio.run(run_mcp_server())

def cli_main():
    app()

if __name__ == "__main__":
    cli_main()
