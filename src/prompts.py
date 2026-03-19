"""Prompt builder: loads system_prompt.md and substitutes placeholders."""

from pathlib import Path

import yaml

_PROMPT_PATH = Path(__file__).parent / "system_prompt.md"


def build_prompt(skills: dict, job_description: str, cv_template: str) -> tuple[str, str]:
    """Build the LLM prompt from the system prompt template and runtime data.

    Args:
        skills: Parsed skills.yaml content.
        job_description: The job posting text provided by the user.
        cv_template: Raw content of cv_template.tex.

    Returns:
        A tuple of (system_prompt, user_message) ready for the LLM API.
    """
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    skills_yaml = yaml.dump(skills, allow_unicode=True, default_flow_style=False)
    system_prompt = (
        template
        .replace("<<cv_template>>", cv_template)
        .replace("<<skills_yaml>>", skills_yaml)
    )
    user_message = f"Descrição da vaga:\n\n{job_description}"
    return system_prompt, user_message
