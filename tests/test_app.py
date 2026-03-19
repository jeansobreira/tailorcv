"""Tests for the FastAPI application endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(mocker):
    """TestClient with generate_cv and compile_tex mocked."""
    mocker.patch("main.load_skills", return_value={})
    mocker.patch("main.build_prompt", return_value=("sys", "usr"))
    import app as app_module
    return TestClient(app_module.app)


def test_get_root_returns_html(client: TestClient) -> None:
    """GET / serves the frontend index.html."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_generate_returns_tex_and_pdf(client: TestClient, mocker) -> None:
    """POST /generate returns tex_content and pdf_base64 on success."""
    mocker.patch("app.generate_cv", return_value=("\\newcommand{\\cvNome}{Jean}", "FAKEB64"))

    response = client.post("/generate", json={"job_description": "Engenheiro"})

    assert response.status_code == 200
    data = response.json()
    assert data["tex_content"] == "\\newcommand{\\cvNome}{Jean}"
    assert data["pdf_base64"] == "FAKEB64"


def test_generate_returns_500_on_pdflatex_failure(client: TestClient, mocker) -> None:
    """POST /generate returns 500 when pdflatex raises RuntimeError."""
    mocker.patch("app.generate_cv", side_effect=RuntimeError("pdflatex falhou"))

    response = client.post("/generate", json={"job_description": "Engenheiro"})

    assert response.status_code == 500
    assert "pdflatex falhou" in response.json()["detail"]


def test_compile_returns_pdf_base64(client: TestClient, mocker) -> None:
    """POST /compile returns pdf_base64 on success."""
    mocker.patch("app.compile_tex", return_value="RECOMPILEDB64")

    response = client.post("/compile", json={"tex_content": "\\newcommand{\\cvNome}{Jean}"})

    assert response.status_code == 200
    assert response.json()["pdf_base64"] == "RECOMPILEDB64"


def test_compile_returns_500_on_pdflatex_failure(client: TestClient, mocker) -> None:
    """POST /compile returns 500 when pdflatex raises RuntimeError."""
    mocker.patch("app.compile_tex", side_effect=RuntimeError("pdflatex falhou"))

    response = client.post("/compile", json={"tex_content": "bad tex"})

    assert response.status_code == 500
    assert "pdflatex falhou" in response.json()["detail"]
