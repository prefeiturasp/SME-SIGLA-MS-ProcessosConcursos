"""Testes unitários dos serializers de autorizações publicadas."""

import pytest

from autorizacoes.models import AutorizacaoPublicada
from autorizacoes.serializers import (
    AutorizacaoPublicadaSerializer,
    AutorizacoesPublicadasTotalSerializer,
)
from cargos.models import Cargo

pytestmark = pytest.mark.django_db


def test_autorizacao_serializer_fields():
    """Serializer completo expõe os campos esperados."""
    obj = AutorizacaoPublicada.objects.create()
    data = AutorizacaoPublicadaSerializer(obj).data
    for field in [
        "uuid",
        "cargo",
        "autorizacoes",
        "data_autorizacao",
        "observacao",
        "criado_em",
        "atualizado_em",
    ]:
        assert field in data


def test_autorizacao_create_with_valid_cargo():
    """Create resolve cargo por UUID."""
    cargo = Cargo.objects.create(nome="Teste")
    serializer = AutorizacaoPublicadaSerializer(
        data={
            "cargo": str(cargo.uuid),
            "autorizacoes": 3,
            "observacao": "Obs",
        }
    )
    assert serializer.is_valid(), serializer.errors
    obj = serializer.save()
    assert obj.cargo == cargo
    assert obj.autorizacoes == 3


def test_autorizacao_create_sem_cargo():
    """Create permite cargo nulo."""
    serializer = AutorizacaoPublicadaSerializer(
        data={"autorizacoes": 1, "observacao": ""}
    )
    assert serializer.is_valid(), serializer.errors
    obj = serializer.save()
    assert obj.cargo is None


def test_autorizacao_create_cargo_inexistente():
    """Cargo UUID inexistente gera erro de validação no create."""
    from rest_framework.exceptions import ValidationError

    serializer = AutorizacaoPublicadaSerializer(
        data={
            "cargo": "00000000-0000-0000-0000-000000000000",
            "autorizacoes": 1,
        }
    )
    assert serializer.is_valid()
    with pytest.raises(ValidationError):
        serializer.save()


def test_total_serializer_opcional():
    """AutorizacoesPublicadasTotalSerializer aceita payload vazio."""
    serializer = AutorizacoesPublicadasTotalSerializer(data={})
    assert serializer.is_valid(), serializer.errors


def test_total_serializer_com_anos_e_concurso():
    """Total serializer valida concurso_uuid e lista de anos."""
    serializer = AutorizacoesPublicadasTotalSerializer(
        data={
            "concurso_uuid": "11111111-1111-1111-1111-111111111111",
            "anos": [2025, 2026],
        }
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["anos"] == [2025, 2026]
