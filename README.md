# Reshallah
Утилита для решения примитивных вузовских задач по программированию при помощи LLM с поддержкой MCP и сборкой отчётов по ГОСТу через Typst.  Прозиносится как решалА. 

# Установка
1. Поставьте [uv](https://docs.astral.sh/uv/#installation), если ещё не стоит
2. Подключите mcp-сервер.
Если у вас cursor, зайдите в Cursor Settings -> MCP & Integraions -> + New MCP Server
Добавьте в `mcp.json` reshallah. Проверьте статус, должно быть доступно 2 инструмента.
```json
{
  "mcpServers": {
    "reshallah": {
      "command": "uvx git+https://github.com/idutvuk/reshallah mcp"
    }
  }
}
```
В настройках mcp утилита должна загореться зелёным и появиться надпись N tools enabled.
Всё, ваша ллмка может компилировать любой контент 😎
3. Опционально - системно установите Times New Roman, так как он используется для отчётов МИРЭА. Если его не будет - будет использован шрифт LiberationSerif, который типа похож на него, так что ничего страшного

# Также может быть интересно

1. https://github.com/typst-g7-32/modern-g7-32 - typst-compiler для госта, подойдёт много для чего
2. https://github.com/benzlokzik/md2gost md -> gost но рабочий, правда, вроде, заброшенный
3. https://github.com/mirea-ninja/Latex-Template-for-Report-Diploma-Thesis - компилятор отчётов мирэа из LaTeX
4. https://oxydoxy.ardyc.ru/ - md -> gost docx. Выключенный сайт
