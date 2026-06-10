"""Módulo tests/models/test_cargo."""

import pytest

from concursos.models import Cargo

pytestmark = pytest.mark.django_db


def test_cargo_model_fields():
    """Verifica cargo model fields."""
    fields = [field.name for field in Cargo._meta.fields]
    expected_fields = ["uuid", "nome", "codigo", "criado_em", "atualizado_em"]
    for field in expected_fields:
        assert field in fields
