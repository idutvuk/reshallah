import asyncio
import os
import json
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.types as types

from .mirea_report import compile_mirea_report
from .typst_compiler import compile_directory_to_pdf


server = Server("reshallah")


@server.list_prompts()
async def handle_list_prompt_actions() -> list:
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    prompts_path = os.path.join(assets_dir, "prompts.json")
    with open(prompts_path, "r", encoding="utf-8") as f:
        return json.load(f)

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
            description="Compile a MIREA report using the built-in template. Requires a content.typ file in the target directory. The PDF will be saved next to the directory. All paths should be absolute and in OS-like format like 'c:\\\\...' in windows or /home/... in *nix",
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


@server.list_prompts()
async def handle_prompt_action(name: str, arguments: dict) -> list:
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    if name == "reshallah_guidelines":
        guidelines_path = os.path.join(assets_dir, "reshallah_guidelines.md")
        with open(guidelines_path, "r", encoding="utf-8") as f:
            return [{
                "type":"text",
                "text": f.read()
            }]
    elif name == "reshallah_project_structure":
        structure_path = os.path.join(assets_dir, "reshallah_project_structure.md")
        with open(structure_path, "r", encoding="utf-8") as f:
            return [{
                "type":"text",
                "text": f.read()
            }]
    elif name == "reshallah_titlepage_selection":
        titlepage_type = arguments.get("titlepage_type")
        author_name = arguments.get("author_name", "")
        author_group = arguments.get("author_group", "")
        department = arguments.get("department", "")
        save_as_default = arguments.get("save_as_default", False)
        
        if titlepage_type == "none":
            response_text = "Отчет будет создан без титульной страницы."
        elif titlepage_type == "custom":
            response_text = "Будет использована пользовательская титульная страница. Укажите путь к PDF файлу при компиляции."
        elif titlepage_type == "default":
            response_text = "Будет использована стандартная титульная страница."
            if author_name:
                response_text += f"\nИмя автора: {author_name}"
            if author_group:
                response_text += f"\nГруппа: {author_group}"
        elif titlepage_type == "mirea":
            response_text = "Будет использован шаблон титульной страницы МИРЭА."
            if author_name:
                response_text += f"\nИмя автора: {author_name}"
            if author_group:
                response_text += f"\nГруппа: {author_group}"
            if department:
                response_text += f"\nКафедра: {department}"
        else:
            response_text = f"Неизвестный тип титульной страницы: {titlepage_type}"
        
        if save_as_default:
            response_text += "\n\nЭти настройки будут сохранены как стандартные для будущих отчетов."
            
        return [types.TextContent(
            type="text",
            text=response_text
        )]
    else:
        raise ValueError(f"Unknown prompt action: {name}")

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "compile_typst_to_pdf":
        directory_path = arguments.get("directory_path")
        
        if not directory_path:
            raise ValueError("directory_path is required")
        
        try:
            directory_path = os.path.abspath(directory_path)
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            output_pdf_path = compile_directory_to_pdf(directory_path)
            return [types.TextContent(
                type="text", 
                text=f"Successfully compiled Typst document to PDF: {output_pdf_path}"
            )]
        except Exception as e:
            # Re-raise the exception so MCP client receives an error
            raise RuntimeError(f"Error compiling Typst document: {str(e)}") from e
    
    elif name == "compile_mirea_report":
        directory_path = arguments.get("directory_path")
        custom_titlepage = arguments.get("custom_titlepage")
        
        if not directory_path:
            raise ValueError("directory_path is required")
        
        try:
            directory_path = os.path.abspath(directory_path)
            
            if custom_titlepage:
                custom_titlepage = os.path.abspath(custom_titlepage)
                if not os.path.exists(custom_titlepage):
                    raise FileNotFoundError(f"Custom titlepage not found: {custom_titlepage}")
            
            output_pdf_path = compile_mirea_report(
                directory_path, 
                custom_titlepage=custom_titlepage
            )
            return [types.TextContent(
                type="text", 
                text=f"Successfully compiled MIREA report to PDF: {output_pdf_path}"
            )]
        except Exception as e:
            # Re-raise the exception so MCP client receives an error
            raise RuntimeError(f"Error compiling MIREA report: {str(e)}") from e
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def run_mcp_server():
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="reshallah",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )