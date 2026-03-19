"""FastAPI application: serves the frontend and exposes the CV generation API."""

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from main import compile_tex, generate_cv

load_dotenv()

app = FastAPI(title="TailorCV")
app.mount("/static", StaticFiles(directory="frontend"), name="static")


class GenerateRequest(BaseModel):
    job_description: str


class GenerateResponse(BaseModel):
    tex_content: str
    pdf_base64: str


class CompileRequest(BaseModel):
    tex_content: str


class CompileResponse(BaseModel):
    pdf_base64: str


@app.get("/")
async def root():
    """Serve the frontend index page."""
    return FileResponse("frontend/index.html")


@app.post("/generate", response_model=GenerateResponse)
async def generate(payload: GenerateRequest):
    """Call the LLM to produce a tailored CV and compile it to PDF.

    Args:
        payload: Request containing the job description text.

    Returns:
        Generated LaTeX content and the compiled PDF in base64.

    Raises:
        HTTPException: 500 if pdflatex compilation fails.
    """
    try:
        tex_content, pdf_base64 = generate_cv(payload.job_description)
        return GenerateResponse(tex_content=tex_content, pdf_base64=pdf_base64)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compile", response_model=CompileResponse)
async def compile_endpoint(payload: CompileRequest):
    """Recompile user-edited LaTeX and return an updated PDF.

    Args:
        payload: Request containing the edited LaTeX content.

    Returns:
        Recompiled PDF in base64.

    Raises:
        HTTPException: 500 if pdflatex compilation fails.
    """
    try:
        pdf_base64 = compile_tex(payload.tex_content)
        return CompileResponse(pdf_base64=pdf_base64)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
