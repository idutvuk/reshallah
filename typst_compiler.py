# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "typst",
#     "typer",
#     "mcp",
#     "asyncio",
# ]
# ///
from enum import Enum
from typing_extensions import Annotated
import asyncio
import argparse
import sys

import typer
import typst
import tempfile
import shutil
import os
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent
import mcp.types as types

class OutputFormat(str, Enum):
    pdf = "pdf"
    png = "png"
    svg = "svg"

def compile_directory_to_pdf(directory_path: str) -> str:
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory {directory_path} does not exist")
    
    if not os.path.isdir(directory_path):
        raise ValueError(f"{directory_path} is not a directory")
    
    # Найти .typ файл в директории
    typ_files = [f for f in os.listdir(directory_path) if f.endswith(".typ")]
    if not typ_files:
        raise FileNotFoundError(f"No .typ files found in {directory_path}")
    
    typ_file = typ_files[0]
    
    directory_name = os.path.basename(os.path.normpath(directory_path))
    parent_dir = os.path.dirname(os.path.abspath(directory_path))
    output_pdf_path = os.path.join(parent_dir, f"{directory_name}.pdf")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copytree(directory_path, temp_dir, dirs_exist_ok=True)
        
        typ_file_path = os.path.join(temp_dir, typ_file)
        
        output = typst.compile(
            typ_file_path,
            format="pdf",
            ppi=144.0
        )
        
        with open(output_pdf_path, "wb") as output_file:
            output_file.write(output)
    
    return output_pdf_path

def main(
        directory: Annotated[str, typer.Option("--dir", "-d")],
        output: Annotated[str, typer.Option("--output", "-o")] = "output",
        type_format: Annotated[OutputFormat, typer.Option("--type_output", "-t")] = OutputFormat.pdf.value
):
    outfile_name = f"{output}.{type_format.value}"

    with tempfile.TemporaryDirectory() as temp_dir, open(outfile_name, "wb") as output_file:
        shutil.copytree(directory, temp_dir, dirs_exist_ok=True)
        typ_file = None
        for f in os.listdir(temp_dir):
            if f.endswith(".typ"):
                typ_file = f

        typ_file_path = os.path.join(temp_dir, typ_file)
        output = typst.compile(
            typ_file_path,
            format=type_format.value,
            ppi=144.0
        )

        output_file.write(output)
        typer.echo(f"compiled, output at {outfile_name}")


server = Server("typst-compiler")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="compile_typst_to_pdf",
            description="Compile a Typst document directory to PDF. The PDF will be saved next to the directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory containing .typ files to compile"
                    }
                },
                "required": ["directory_path"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "compile_typst_to_pdf":
        directory_path = arguments.get("directory_path")
        
        if not directory_path:
            return [types.TextContent(
                type="text",
                text="Error: directory_path is required"
            )]
        
        try:
            output_pdf_path = compile_directory_to_pdf(directory_path)
            return [types.TextContent(
                type="text", 
                text=f"Successfully compiled Typst document to PDF: {output_pdf_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error compiling Typst document: {str(e)}"
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def run_mcp_server(port: int = 41434):
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="typst-compiler",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Typst Compiler with MCP Server")
    parser.add_argument("--mcp", action="store_true", help="Run as MCP server")
    parser.add_argument("--port", type=int, default=41434, help="Port for MCP server")
    
    args, unknown = parser.parse_known_args()
    
    if args.mcp:
        asyncio.run(run_mcp_server(args.port))
    else:
        # Restore original typer arguments for CLI mode
        sys.argv = [sys.argv[0]] + unknown
        typer.run(main)
