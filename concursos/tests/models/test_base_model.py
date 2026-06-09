"""Módulo tests/models/test_base_model."""
import uuid

import pytest
from django.utils import timezone

from concursos.models import Cargo

pytestmark = pytest.mark.django_db


def test_base_model_fields():
    """Verifica base model fields.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cargo = Cargo.objects.create(nome="Teste")
    assert cargo.uuid is not None
    assert cargo.criado_em is not None
    assert cargo.atualizado_em is not None
    assert isinstance(cargo.uuid, uuid.UUID)
    assert isinstance(cargo.criado_em, timezone.datetime)
    assert isinstance(cargo.atualizado_em, timezone.datetime)
