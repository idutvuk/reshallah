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
async def compile_typst(file: UploadFile):
    tmpdir = f"/tmp/{uuid.uuid4()}"
    os.makedirs(tmpdir, exist_ok=True)

    filepath = os.path.join(tmpdir, file.filename)
    with open(filepath, "wb") as f:
        f.write(await file.read())

    if file.filename.endswith(".zip"):
        subprocess.run(["unzip", filepath, "-d", tmpdir], check=True)

    pdf_path = os.path.join(tmpdir, "output.pdf")
    print(f"typst compile {os.path.join(tmpdir, file.filename)} {pdf_path}")
    os.system(f"typst compile {os.path.join(tmpdir, file.filename)} {pdf_path}")

    return FileResponse(pdf_path, media_type="application/pdf", filename="output.pdf")

mcp = FastApiMCP(app)

mcp.mount_http()