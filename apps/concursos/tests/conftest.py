"""Fixtures do app concursos (compartilhadas com os demais apps)."""

import pytest

from concursos.tests.fixtures import *  # noqa: F403
from concursos.tests.fixtures import apply_cargo_repository_compat


@pytest.fixture(autouse=True)
def _compat_cargo_repository_obter_modelo(monkeypatch):
    """Compat dos serializers sem ``obter_modelo*`` no repository."""
    apply_cargo_repository_compat(monkeypatch)
