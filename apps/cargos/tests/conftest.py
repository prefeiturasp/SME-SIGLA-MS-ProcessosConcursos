"""Fixtures do app cargos."""

import pytest

from concursos.tests.fixtures import *  # noqa: F403
from concursos.tests.fixtures import apply_cargo_repository_compat


@pytest.fixture(autouse=True)
def _compat_cargo_repository_obter_modelo(monkeypatch):
    """Compat dos serializers sem ``obter_modelo*`` no repository."""
    apply_cargo_repository_compat(monkeypatch)


@pytest.fixture
def cargo_data():
    """Fixture para dados de cargo válidos."""
    return {"nome": "Novo Cargo de Teste"}


@pytest.fixture
def cargo_data_invalid():
    """Fixture para dados de cargo inválidos."""
    return {"nome": ""}  # Nome vazio é inválido


@pytest.fixture
def cargo_data_long_name():
    """Fixture para dados de cargo com nome muito longo."""
    return {"nome": "A" * 201}  # Mais que max_length=200
