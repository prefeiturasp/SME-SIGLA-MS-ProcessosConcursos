"""Módulo tests/models/test_autorizacao_publicada."""
import pytest

from concursos.models import AutorizacaoPublicada, Cargo

pytestmark = pytest.mark.django_db


def test_autorizacao_publicada_model_fields():
    """Verifica autorizacao publicada model fields.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    fields = [field.name for field in AutorizacaoPublicada._meta.fields]
    expected_fields = [
        "uuid",
        "cargo",
        "autorizacoes",
        "data_autorizacao",
        "observacao",
        "criado_em",
        "atualizado_em",
    ]
    for field in expected_fields:
        assert field in fields


def test_autorizacao_publicada_str():
    """Verifica autorizacao publicada str.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    obj = AutorizacaoPublicada.objects.create()
    assert str(obj).startswith("Autorização ")


def test_autorizacao_publicada_with_cargo():
    """Verifica autorizacao publicada with cargo.
    
    Returns:
        Nenhum valor; valida comportamento via asserções.
    
    Raises:
        Nenhuma exceção específica documentada.
    """
    cargo = Cargo.objects.create(nome="Teste Cargo")
    obj = AutorizacaoPublicada.objects.create(cargo=cargo, autorizacoes=10)
    assert obj.cargo == cargo
    assert obj.autorizacoes == 10
