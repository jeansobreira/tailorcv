"""Tests for prompts.build_prompt."""

import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest


def test_build_prompt_substitutes_cv_template(tmp_path: Path) -> None:
    """build_prompt replaces <<cv_template>> with the template content."""
    fake_prompt = "BEFORE <<cv_template>> AFTER <<skills_yaml>>"
    prompt_file = tmp_path / "system_prompt.md"
    prompt_file.write_text(fake_prompt, encoding="utf-8")

    with patch("prompts._PROMPT_PATH", prompt_file):
        from prompts import build_prompt

        system_prompt, _ = build_prompt(
            skills={}, job_description="vaga", cv_template="MY_TEMPLATE"
        )

    assert "MY_TEMPLATE" in system_prompt
    assert "<<cv_template>>" not in system_prompt


def test_build_prompt_substitutes_skills_yaml(tmp_path: Path) -> None:
    """build_prompt serialises skills dict and replaces <<skills_yaml>>."""
    fake_prompt = "BEFORE <<cv_template>> AFTER <<skills_yaml>>"
    prompt_file = tmp_path / "system_prompt.md"
    prompt_file.write_text(fake_prompt, encoding="utf-8")

    with patch("prompts._PROMPT_PATH", prompt_file):
        from prompts import build_prompt

        system_prompt, _ = build_prompt(
            skills={"nome": "Jean"}, job_description="vaga", cv_template="tpl"
        )

    assert "nome: Jean" in system_prompt
    assert "<<skills_yaml>>" not in system_prompt


def test_build_prompt_user_message_contains_job_description(tmp_path: Path) -> None:
    """build_prompt wraps the job description in the user message."""
    prompt_file = tmp_path / "system_prompt.md"
    prompt_file.write_text("<<cv_template>> <<skills_yaml>>", encoding="utf-8")

    with patch("prompts._PROMPT_PATH", prompt_file):
        from prompts import build_prompt

        _, user_message = build_prompt(
            skills={}, job_description="Engenheiro de Dados", cv_template="tpl"
        )

    assert "Engenheiro de Dados" in user_message
