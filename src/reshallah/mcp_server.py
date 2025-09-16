import asyncio
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.types as types

from .mirea_report import compile_mirea_report
from .typst_compiler import compile_directory_to_pdf


# Создаем экземпляр сервера
server = Server("typst-compiler")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Возвращает список доступных MCP инструментов."""
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


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Обрабатывает вызовы MCP инструментов."""
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


async def run_mcp_server():
    """Запускает MCP сервер."""
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