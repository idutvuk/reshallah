from http.client import HTTPResponse

from fastapi import FastAPI, UploadFile, Form
from fastapi_mcp import FastApiMCP
from fastapi.responses import FileResponse
import subprocess
import os
import uuid

app = FastAPI(title="Typst MCP Server")


@app.get("/")
async def root():
    return {"status": "hello"}


@app.post("/compile")
async def compile_typst(file: UploadFile, main: str = Form("main.typ")):
    # создаём временную папку
    tmpdir = f"/tmp/{uuid.uuid4()}"
    os.makedirs(tmpdir, exist_ok=True)

    # сохраняем архив или один .typ файл
    filepath = os.path.join(tmpdir, file.filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())

    # если передали zip с проектом — разархивировать
    if file.filename.endswith(".zip"):
        subprocess.run(["unzip", filepath, "-d", tmpdir], check=True)

    pdf_path = os.path.join(tmpdir, "output.pdf")
    subprocess.run(["typst", "compile", os.path.join(tmpdir, main), pdf_path], check=True)

    return FileResponse(pdf_path, media_type="application/pdf", filename="output.pdf")

mcp = FastApiMCP(app)

# Mount the MCP server directly to your FastAPI app
mcp.mount_http()