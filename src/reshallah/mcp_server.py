import asyncio
import os
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
import mcp.types as types

from .mirea_report import compile_mirea_report
from .typst_compiler import compile_directory_to_pdf


server = Server("reshallah")


@server.list_prompts()
async def handle_list_prompt_actions() -> list:
    return [
        {
            "name":"reshallah_guidelines",
            "description":"Instructions for using the reshallah system and its pipeline structure",
            "promptSchema":{
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name":"reshallah_project_structure",
            "description":"Guidelines for project structure in reshallah",
            "promptSchema":{
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name":"reshallah_titlepage_selection",
            "description":"Choose a titlepage type for your report",
            "promptSchema":{
                "type": "object",
                "properties": {
                    "titlepage_type": {
                        "type": "string",
                        "description": "Type of titlepage to use",
                        "enum": ["none", "custom", "default", "mirea"]
                    },
                    "author_name": {
                        "type": "string",
                        "description": "Optional: Author name for the titlepage"
                    },
                    "author_group": {
                        "type": "string",
                        "description": "Optional: Author's group/class for the titlepage"
                    },
                    "department": {
                        "type": "string",
                        "description": "Optional: Department name for the titlepage"
                    },
                    "save_as_default": {
                        "type": "boolean",
                        "description": "Optional: Save these settings as default for future reports"
                    }
                },
                "required": ["titlepage_type"]
            }
        },
    ]

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
    if name == "reshallah_guidelines":
        return [{
            "type":"text",
            "text":"""
# Руководство по использованию Reshallah

## Общие инструкции

Reshallah - это Python пакет для автоматизации создания отчетов по практическим заданиям, который можно подключить к MCP или использовать через CLI.

## Этапы рабочего процесса

0. **Установка и подготовка**:
   - Добавьте в `mcp.json` следующую конфигурацию:
   ```json
   "mcpServers": {
     "reshallah": {
       "command": "uvx git+https://github.com/idutvuk/reshallah mcp"
     }
   }
   ```

1. **Создание задания**:
   - Создайте входное задание в файле `input/tasks.md` в формате todolist

2. **Решение задач**:
   - Решите задачи и создайте файлы в директории `solution/pracN/`
   - Создайте тесты для проверки решений
   - Убедитесь, что все решения работают корректно

3. **Форматирование и очистка кода**:
   - Очистите код от лишних комментариев
   - Отформатируйте код для презентации

4. **Создание отчета**:
   - Сформируйте отчет `content.typ` в директории `output/`
   - Скомпилируйте отчет с помощью соответствующего инструмента

## Типы титульных страниц

- **none**: без титульной страницы
- **custom**: пользовательская PDF титульная страница
- **default**: простая титульная страница
- **mirea**: титульная страница по шаблону МИРЭА

## Рекомендации

- Делайте коммит после каждого этапа
- Сохраняйте структуру проекта согласно документации
- Используйте соответствующие инструменты компиляции для разных типов отчетов
"""
        }]
    elif name == "reshallah_project_structure":
        return [{
            "type":"text",
            "text":"""
# Структура проекта Reshallah

```
project/
  ├── input/
  │   └── tasks.md           # Описание заданий в формате todolist
  │
  ├── solution/
  │   ├── prac1/
  │   │   ├── task1.lang     # Решение задачи 1 практики 1
  │   │   ├── task1_test.lang # Тест для задачи 1
  │   │   ├── task2.lang     # Решение задачи 2 практики 1
  │   │   └── ...
  │   │
  │   ├── prac2/
  │   │   ├── task1.lang
  │   │   └── ...
  │   │
  │   └── ...
  │
  └── output/
      ├── content.typ        # Основной контент отчета
      ├── additional_typsts.typ # Дополнительные файлы Typst
      ├── resource1.png      # Ресурсы (изображения и пр.)
      ├── resource2.media
      ├── ...
      └── output.pdf         # Итоговый скомпилированный отчет
```

## Пояснения к структуре

- **input/**: Директория для входных заданий
  - `tasks.md`: Файл с описанием заданий, которые нужно выполнить

- **solution/**: Директория для решений заданий
  - `pracN/`: Поддиректория для практики номер N
    - `taskM.lang`: Файл с решением задачи M (где .lang - расширение языка программирования)
    - `taskM_test.lang`: Тестовый файл для задачи M

- **output/**: Директория для выходных файлов отчета
  - `content.typ`: Основной файл с контентом отчета в формате Typst. Должен содержать только структуру и текст, без стилей и других данных. Содержание, титульники и прочее генерируется автоматически.
  - Дополнительные файлы и ресурсы для отчета
  - `output.pdf`: Финальный скомпилированный отчет в формате PDF
FORBIDDEN, ЗАПРЕЩЕНО вставлять в content.typ #set page, #set text #set par и другие директивы, которые влияют на стили и структуру страницы.
"""
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