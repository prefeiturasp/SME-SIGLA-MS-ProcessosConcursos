"""Módulo tests/models/test_concurso."""

import pytest

from concursos.models import Concurso

pytestmark = pytest.mark.django_db


def test_concurso_model_fields():
    """Verifica concurso model fields."""
    fields = [field.name for field in Concurso._meta.fields]
    expected_fields = ["uuid", "nome", "criado_em", "atualizado_em"]
    for field in expected_fields:
        assert field in fields
