# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "typst",
#     "typer",
# ]
# ///
from enum import Enum
from typing import List
from typing_extensions import Annotated

import typer
import typst
import tempfile
import shutil
import os

class OutputFormat(str, Enum):
    pdf = "pdf"
    png = "png"
    svg = "svg"

def main(
        directory: Annotated[str, typer.Option("--dir", "-d")] = ".",
        files: Annotated[List[str], typer.Option("--files", "-f")] = (),
        output: Annotated[str, typer.Option("--output", "-o")] = "output",
        type_format: Annotated[OutputFormat, typer.Option("--type_output", "-t")] = OutputFormat.pdf.value
):
    outfile_name = f"{output}.{type_format.value}"

    with tempfile.TemporaryDirectory() as temp_dir, open(outfile_name, "wb") as output_file:
        if directory:
            shutil.copytree(directory, temp_dir, dirs_exist_ok=True)
            typ_file = [f for f in os.listdir(temp_dir) if f.endswith(".typ")][0]
        elif len(files):
            typer.echo(f"{files}, {len(files)}, {type(files)}")
            for f in files:
                shutil.copy(f, temp_dir)
                if f.endswith(".typ"):
                    typ_file = f
        else:
            typer.echo("no --directory or --files provided, lemme try to compile current directory")
            shutil.copytree(os.getcwd(), temp_dir, dirs_exist_ok=True)
            typ_file = [f for f in os.listdir(temp_dir) if f.endswith(".typ")][0]
        
        output = typst.compile(
            os.path.join(temp_dir, typ_file),
            format=type_format.value,
            ppi=144.0
        )

        output_file.write(output)
        typer.echo(f"compiled, output at {outfile_name}")


if __name__ == "__main__":
    typer.run(main)
