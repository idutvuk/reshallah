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


def compile_mirea_report(directory_path: str, custom_titlepage: str = None) -> str:
    """Compile MIREA report by copying template and requiring content.typ file."""
    # Normalize the directory path
    directory_path = os.path.abspath(directory_path)
    
    # Check if content.typ exists in the directory
    content_typ_path = os.path.join(directory_path, "content.typ")
    if not os.path.exists(content_typ_path):
        raise FileNotFoundError(f"content.typ file not found at {content_typ_path}. Directory path: {directory_path}. This is required for MIREA reports.")
    
    # Get the path to the mirea_report_template folder
    current_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(current_dir, "assets", "mirea_report_template")
    
    if not os.path.exists(template_dir):
        raise FileNotFoundError(f"MIREA report template not found at {template_dir}")
    
    directory_name = os.path.basename(os.path.normpath(directory_path))
    parent_dir = os.path.dirname(os.path.abspath(directory_path))
    output_pdf_path = os.path.join(parent_dir, f"{directory_name}.pdf")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # First copy the template files
        for item in os.listdir(template_dir):
            src = os.path.join(template_dir, item)
            dst = os.path.join(temp_dir, item)
            if os.path.isfile(src):
                shutil.copy2(src, dst)
            elif os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
        
        # Then copy the user's content.typ file (overwriting template's content.typ)
        shutil.copy2(content_typ_path, os.path.join(temp_dir, "content.typ"))
        
        # Copy any other files from user's directory (but not overwriting main template files)
        template_files = {"main.typ", "simple-template.typ", "listing_examples.typ", "main_example.typ", "mirea-logo.png", "refs.bib", "simple_listing_example.typ", "test.typ"}
        for item in os.listdir(directory_path):
            if item not in template_files and item != "content.typ":  # Skip content.typ as it's already copied
                src = os.path.join(directory_path, item)
                dst = os.path.join(temp_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)
        
        # Handle custom titlepage if provided
        if custom_titlepage and os.path.exists(custom_titlepage):
            # Copy PDF file to temp directory
            titlepage_filename = os.path.basename(custom_titlepage)
            titlepage_temp_path = os.path.join(temp_dir, titlepage_filename)
            shutil.copy2(custom_titlepage, titlepage_temp_path)
            
            # Read main.typ and add titlepage inclusion
            main_typ_path = os.path.join(temp_dir, "main.typ")
            with open(main_typ_path, 'r', encoding='utf-8') as f:
                main_content = f.read()
            
            # Add muchpdf import and titlepage inclusion at the beginning
            pdf_include = (
                # f'#set page (margin: (left: 2cm, right: 2cm, top: 2cm, bottom: 2cm))\n'
                          f'#import "@preview/muchpdf:0.1.0": muchpdf\n\n'
                          f'#muchpdf(read("{titlepage_filename}", encoding: none))\n\n')
            
            main_content = pdf_include + main_content
            
            with open(main_typ_path, 'w', encoding='utf-8') as f:
                f.write(main_content)
        
        # Compile using main.typ
        typ_file_path = os.path.join(temp_dir, "main.typ")
        
        output = typst.compile(
            typ_file_path,
            format="pdf",
            ppi=144.0
        )
        
        with open(output_pdf_path, "wb") as output_file:
            output_file.write(output)
    
    return output_pdf_path


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
            pdf_include = (
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


# Создаем экземпляр Typer приложения
app = typer.Typer()


@app.command()
def compile(
        directory: Annotated[str, typer.Option("--dir", "-d")],
        output: Annotated[str, typer.Option("--output", "-o")] = "output",
):
    """Compile a Typst document directory to PDF"""
    main(directory, output)


@app.command()
def mcp(
        port: Annotated[int, typer.Option("--port", "-p")] = 41434,
):
    """Run as MCP server"""
    asyncio.run(run_mcp_server(port))


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
            name="compile_mirea_report",
            description="Compile a MIREA report using the built-in template. Requires a content.typ file in the target directory. The PDF will be saved next to the directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "Path to the directory containing content.typ file"
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
                text=f"Error compiling Typst document: {str(e)}, {type(e)}"
            )]
    
    elif name == "compile_mirea_report":
        directory_path = arguments.get("directory_path")
        custom_titlepage = arguments.get("custom_titlepage")
        
        if not directory_path:
            return [types.TextContent(
                type="text",
                text="Error: directory_path is required"
            )]
        
        try:
            output_pdf_path = compile_mirea_report(
                directory_path, 
                custom_titlepage=custom_titlepage
            )
            return [types.TextContent(
                type="text", 
                text=f"Successfully compiled MIREA report to PDF: {output_pdf_path}"
            )]
        except Exception as e:
            return [types.TextContent(
                type="text",
                text=f"Error compiling MIREA report: {str(e)}"
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

def cli_main():
    """Entry point for the CLI application"""
    app()

if __name__ == "__main__":
    cli_main()
