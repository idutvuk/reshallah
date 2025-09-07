from http.client import HTTPResponse

from fastapi import FastAPI, UploadFile, Form
from fastapi_mcp import FastApiMCP
from fastapi.responses import FileResponse, JSONResponse
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
    
    typst_path = "/usr/bin/typst"
    typst_cmd = None
    
    try:
        result = subprocess.run(
            [typst_path, "compile", os.path.join(tmpdir, file.filename), pdf_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Compilation error",
                    "stderr": result.stderr,
                    "stdout": result.stdout,
                    "returncode": result.returncode
                }
            )
        
        if not os.path.exists(pdf_path):
            return JSONResponse(
                status_code=500,
                content={
                    "error": "somehow pdf was not created",
                    "stderr": result.stderr,
                    "stdout": result.stdout
                }
            )
        
        return FileResponse(pdf_path, media_type="application/pdf", filename="output.pdf")
        
    except subprocess.TimeoutExpired:
        return JSONResponse(
            status_code=408,
            content={"error": "compile timeout"}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"unexp egor during compilation: {str(e)}"}
        )

mcp = FastApiMCP(app)

mcp.mount_http()