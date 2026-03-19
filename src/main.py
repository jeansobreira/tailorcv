"""Orchestrator: skills + job description → LLM → LaTeX → PDF."""

import base64
import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

from llm import call_llm as _call_llm
from prompts import build_prompt

BASE_DIR = Path(__file__).parent.parent  # project root — data files live here


def load_skills(path: str = "skills.yaml") -> dict:
    """Load and parse the skills YAML file.

    Args:
        path: Relative path to the YAML file from BASE_DIR.

    Returns:
        Parsed skills as a dict.
    """
    with open(BASE_DIR / path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _strip_fences(tex_content: str) -> str:
    """Remove markdown code fences if the LLM wrapped the output.

    Args:
        tex_content: Raw LLM response.

    Returns:
        Clean LaTeX string without fence markers.
    """
    content = tex_content.strip()
    if content.startswith("```latex"):
        content = content[len("```latex"):].lstrip("\n")
    if content.startswith("```"):
        content = content[3:].lstrip("\n")
    if content.endswith("```"):
        content = content[:-3].rstrip()
    return content


def _run_pdflatex(tmp_dir: Path) -> bytes:
    """Compile cv_template.tex inside tmp_dir and return the PDF bytes.

    Expects cv_content.tex to already be written in tmp_dir.

    Args:
        tmp_dir: Temporary directory with cv_content.tex present.

    Returns:
        Raw bytes of the compiled PDF.

    Raises:
        RuntimeError: If pdflatex exits with a non-zero return code.
    """
    shutil.copy(BASE_DIR / "cv_template.tex", tmp_dir / "cv_template.tex")
    result = subprocess.run(
        ["pdflatex", "--interaction=nonstopmode", "cv_template.tex"],
        cwd=tmp_dir,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pdflatex falhou:\n{result.stdout}")
    return (tmp_dir / "cv_template.pdf").read_bytes()


def generate_cv(job_description: str) -> tuple[str, str]:
    """Generate a tailored CV from the job description.

    Loads skills, calls the LLM to produce filled LaTeX commands,
    then compiles the PDF.

    Args:
        job_description: The job posting text from the user.

    Returns:
        A tuple of (tex_content, pdf_base64) where tex_content is the
        LLM-generated LaTeX and pdf_base64 is the compiled PDF in base64.

    Raises:
        RuntimeError: If pdflatex compilation fails.
    """
    skills = load_skills()
    cv_template = (BASE_DIR / "cv_template.tex").read_text(encoding="utf-8")
    system_prompt, user_message = build_prompt(skills, job_description, cv_template)

    tex_content = _strip_fences(_call_llm(system_prompt, user_message))

    tmp_dir = Path(tempfile.mkdtemp())
    try:
        (tmp_dir / "cv_content.tex").write_text(tex_content, encoding="utf-8")
        pdf_bytes = _run_pdflatex(tmp_dir)
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        return tex_content, pdf_base64
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def compile_tex(tex_content: str) -> str:
    """Recompile a user-edited LaTeX snippet and return the PDF in base64.

    Args:
        tex_content: Edited LaTeX content (cv_content.tex body).

    Returns:
        Base64-encoded PDF string.

    Raises:
        RuntimeError: If pdflatex compilation fails.
    """
    tmp_dir = Path(tempfile.mkdtemp())
    try:
        (tmp_dir / "cv_content.tex").write_text(tex_content, encoding="utf-8")
        pdf_bytes = _run_pdflatex(tmp_dir)
        return base64.b64encode(pdf_bytes).decode("utf-8")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
