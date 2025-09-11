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


def compile_directory_to_pdf(directory_path: str, content_file: str = None, content_directory: str = None, custom_titlepage: str = None) -> str:
    typ_file = next(f for f in os.listdir(directory_path) if f.endswith("main.typ"))
    
    directory_name = os.path.basename(os.path.normpath(directory_path))
    parent_dir = os.path.dirname(os.path.abspath(directory_path))
    output_pdf_path = os.path.join(parent_dir, f"{directory_name}.pdf")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        shutil.copytree(directory_path, temp_dir, dirs_exist_ok=True)
        
        # Если передан content_file, копируем его как content.typ
        if content_file and os.path.exists(content_file):
            shutil.copy2(content_file, os.path.join(temp_dir, "content.typ"))
        
        # Если передана content_directory, копируем все содержимое и создаем content.typ
        if content_directory and os.path.exists(content_directory):
            # Копируем все файлы из content_directory в temp_dir
            for item in os.listdir(content_directory):
                src = os.path.join(content_directory, item)
                dst = os.path.join(temp_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
            
            # Ищем content.typ в content_directory
            content_typ_path = os.path.join(content_directory, "content.typ")
            if os.path.exists(content_typ_path):
                shutil.copy2(content_typ_path, os.path.join(temp_dir, "content.typ"))
        
        # Если передан custom_titlepage (PDF файл), добавляем его в начало документа
        if custom_titlepage and os.path.exists(custom_titlepage):
            # Копируем PDF файл в временную директорию
            titlepage_filename = os.path.basename(custom_titlepage)
            titlepage_temp_path = os.path.join(temp_dir, titlepage_filename)
            shutil.copy2(custom_titlepage, titlepage_temp_path)
            
            # Читаем основной файл main.typ
            main_typ_path = os.path.join(temp_dir, typ_file)
            with open(main_typ_path, 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            # Добавляем импорт muchpdf и включение PDF в самое начало файла
            pdf_include = (f'#set page (margin: (left: 2cm, right:2 2cm, top: 2cm, bottom: 2cm))\n'
                           f'#import "@preview/muchpdf:0.1.0": muchpdf\n\n'
                           f'#muchpdf(read("{titlepage_filename}", encoding: none))\n\n'
                           )
            
            # Добавляем в начало файла перед всеми остальными декларациями
            main_content = pdf_include + main_content
            
            # Записываем обновленный main.typ
            with open(main_typ_path, 'w', encoding='utf-8') as f:
                f.write(main_content)
        
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
):
    """ cli tool"""
    outfile_name = f"{output}.pdf"

    with tempfile.TemporaryDirectory() as temp_dir, open(outfile_name, "wb") as output_file:
        shutil.copytree(directory, temp_dir, dirs_exist_ok=True)
        typ_file = None
        for f in os.listdir(temp_dir):
            if f.endswith(".typ"):
                typ_file = f

        typ_file_path = os.path.join(temp_dir, typ_file)
        output = typst.compile(
            typ_file_path,
            format="pdf",
            ppi=144.0
        )

        output_file.write(output)
        typer.echo(f"compiled, output at {outfile_name}")


server = Server("typst-compiler")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
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
        ),
        types.Tool(
            name="compile_typst_with_content",
            description="Compile a Typst document directory to PDF with additional content.typ file. The PDF will be saved next to the directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory containing .typ files to compile"
                    },
                    "content_file": {
                        "type": "string",
                        "description": "Path to the content.typ file to be included in the center of main.typ"
                    }
                },
                "required": ["directory_path", "content_file"]
            }
        ),
        types.Tool(
            name="compile_typst_advanced",
            description="Compile a Typst document with advanced options: custom PDF titlepage, content directory with images, etc. All input paths should be absolute",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory containing .typ files to compile"
                    },
                    "content_file": {
                        "type": "string",
                        "description": "Optional: Path to the content.typ file to be included"
                    },
                    "content_directory": {
                        "type": "string", 
                        "description": "Optional: Path to directory containing content.typ and images/resources"
                    },
                    "custom_titlepage": {
                        "type": "string",
                        "description": "Optional: Path to custom titlepage PDF file to include at the beginning of the document"
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
    
    elif name == "compile_typst_with_content":
        directory_path = arguments.get("directory_path")
        content_file = arguments.get("content_file")
        
        if not directory_path:
            return [types.TextContent(
                type="text",
                text="Error: directory_path is required"
            )]
        
        if not content_file:
            return [types.TextContent(
                type="text",
                text="Error: content_file is required"
            )]
        
        try:
            output_pdf_path = compile_directory_to_pdf(directory_path, content_file)
            return [types.TextContent(
                type="text", 
                text=f"Successfully compiled Typst document with content to PDF: {output_pdf_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error compiling Typst document with content: {str(e)}"
            )]
    
    elif name == "compile_typst_advanced":
        directory_path = arguments.get("directory_path")
        content_file = arguments.get("content_file")
        content_directory = arguments.get("content_directory")
        custom_titlepage = arguments.get("custom_titlepage")
        
        if not directory_path:
            return [types.TextContent(
                type="text",
                text="Error: directory_path is required"
            )]
        
        try:
            output_pdf_path = compile_directory_to_pdf(
                directory_path, 
                content_file=content_file,
                content_directory=content_directory,
                custom_titlepage=custom_titlepage
            )
            return [types.TextContent(
                type="text", 
                text=f"Successfully compiled Typst document with advanced options to PDF: {output_pdf_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error compiling Typst document with advanced options: {str(e)}"
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
