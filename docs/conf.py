"""Configuração do Sphinx para o Módulo Processos de Concursos."""

project = "Módulo Processos de Concursos"
author = "SME - SIGLA"
copyright = "2026, SME - SIGLA"

extensions: list[str] = []

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "pt_BR"

html_theme = "alabaster"

html_theme_options = {
    "description": (
        "Documentação do módulo de processos de concursos da SIGLA."
    ),
    "github_button": False,
}
