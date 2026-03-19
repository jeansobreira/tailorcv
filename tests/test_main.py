"""Tests for main.py orchestrator functions."""

import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import main


def test_load_skills_returns_dict() -> None:
    """load_skills parses skills.yaml and returns a dict."""
    skills = main.load_skills()
    assert isinstance(skills, dict)
    assert len(skills) > 0


def test_load_skills_custom_path(tmp_path: Path) -> None:
    """load_skills reads an arbitrary YAML file when path is overridden."""
    yaml_file = tmp_path / "test_skills.yaml"
    yaml_file.write_text("nome: Teste\n", encoding="utf-8")

    with patch("main.BASE_DIR", tmp_path):
        skills = main.load_skills("test_skills.yaml")

    assert skills == {"nome": "Teste"}


# --- _strip_fences -----------------------------------------------------------

def test_strip_fences_removes_latex_fence() -> None:
    """_strip_fences removes ```latex ... ``` wrappers."""
    raw = "```latex\n\\newcommand{\\cvNome}{Jean}\n```"
    assert main._strip_fences(raw) == "\\newcommand{\\cvNome}{Jean}"


def test_strip_fences_removes_plain_fence() -> None:
    """_strip_fences removes plain ``` wrappers."""
    raw = "```\n\\newcommand{\\cvNome}{Jean}\n```"
    assert main._strip_fences(raw) == "\\newcommand{\\cvNome}{Jean}"


def test_strip_fences_leaves_clean_content_unchanged() -> None:
    """_strip_fences does not alter content that has no fences."""
    raw = "\\newcommand{\\cvNome}{Jean}"
    assert main._strip_fences(raw) == raw


# --- _run_pdflatex -----------------------------------------------------------

def test_run_pdflatex_raises_on_nonzero_returncode(tmp_path: Path, mocker) -> None:
    """_run_pdflatex raises RuntimeError when pdflatex fails."""
    base_dir = tmp_path / "base"
    tmp_dir = tmp_path / "work"
    base_dir.mkdir()
    tmp_dir.mkdir()

    (base_dir / "cv_template.tex").write_text("", encoding="utf-8")
    (tmp_dir / "cv_content.tex").write_text("", encoding="utf-8")
    mocker.patch("main.BASE_DIR", base_dir)

    mock_result = MagicMock(returncode=1, stdout="! Undefined control sequence.")
    mocker.patch("main.subprocess.run", return_value=mock_result)

    with pytest.raises(RuntimeError, match="pdflatex falhou"):
        main._run_pdflatex(tmp_dir)


def test_run_pdflatex_returns_pdf_bytes(tmp_path: Path, mocker) -> None:
    """_run_pdflatex returns bytes of the compiled PDF on success."""
    base_dir = tmp_path / "base"
    tmp_dir = tmp_path / "work"
    base_dir.mkdir()
    tmp_dir.mkdir()

    (base_dir / "cv_template.tex").write_text("", encoding="utf-8")
    (tmp_dir / "cv_content.tex").write_text("", encoding="utf-8")
    mocker.patch("main.BASE_DIR", base_dir)

    fake_pdf = b"%PDF-1.4 fake"
    (tmp_dir / "cv_template.pdf").write_bytes(fake_pdf)

    mock_result = MagicMock(returncode=0, stdout="")
    mocker.patch("main.subprocess.run", return_value=mock_result)

    result = main._run_pdflatex(tmp_dir)
    assert result == fake_pdf


# --- generate_cv -------------------------------------------------------------

def _mock_llm(mocker, response_text: str) -> None:
    """Helper: mock _call_llm to return a fixed text response."""
    mocker.patch("main._call_llm", return_value=response_text)


def test_generate_cv_returns_tex_and_base64(mocker) -> None:
    """generate_cv returns (tex_content, pdf_base64) on success."""
    fake_tex = "\\newcommand{\\cvNome}{Jean}"
    fake_pdf = b"%PDF-1.4"

    mocker.patch("main.load_skills", return_value={"nome": "Jean"})
    mocker.patch("main.build_prompt", return_value=("system prompt", "user message"))
    _mock_llm(mocker, fake_tex)
    mocker.patch("main._run_pdflatex", return_value=fake_pdf)

    tex_content, pdf_base64 = main.generate_cv("Engenheiro de Dados")

    assert tex_content == fake_tex
    assert pdf_base64 == base64.b64encode(fake_pdf).decode("utf-8")


def test_generate_cv_strips_fences_from_llm_response(mocker) -> None:
    """generate_cv cleans up markdown fences the LLM may include."""
    fake_pdf = b"%PDF-1.4"

    mocker.patch("main.load_skills", return_value={})
    mocker.patch("main.build_prompt", return_value=("sys", "usr"))
    _mock_llm(mocker, "```latex\n\\newcommand{\\cvNome}{Jean}\n```")
    mocker.patch("main._run_pdflatex", return_value=fake_pdf)

    tex_content, _ = main.generate_cv("vaga")
    assert "```" not in tex_content


# --- compile_tex -------------------------------------------------------------

def test_compile_tex_returns_base64(mocker) -> None:
    """compile_tex recompiles user-edited LaTeX and returns base64 PDF."""
    fake_pdf = b"%PDF-1.4"
    mocker.patch("main._run_pdflatex", return_value=fake_pdf)

    result = main.compile_tex("\\newcommand{\\cvNome}{Jean}")

    assert result == base64.b64encode(fake_pdf).decode("utf-8")


def test_compile_tex_propagates_pdflatex_error(mocker) -> None:
    """compile_tex re-raises RuntimeError from _run_pdflatex."""
    mocker.patch("main._run_pdflatex", side_effect=RuntimeError("pdflatex falhou"))

    with pytest.raises(RuntimeError, match="pdflatex falhou"):
        main.compile_tex("bad tex")
