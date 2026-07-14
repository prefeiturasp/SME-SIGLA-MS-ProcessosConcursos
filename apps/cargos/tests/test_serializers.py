"""Testes unitários dos serializers de cargos."""

import pytest

from cargos.serializers import (
    CargoListSerializer,
    CargoSelectSerializer,
    CargoSerializer,
)

pytestmark = pytest.mark.django_db


def test_cargo_serializer_fields(cargo_analista):
    """Serializer completo expõe uuid, nome e timestamps."""
    data = CargoSerializer(cargo_analista).data
    assert data["nome"] == "Analista de Sistemas"
    assert data["uuid"] == str(cargo_analista.uuid)
    assert "criado_em" in data
    assert "atualizado_em" in data
    assert "codigo" in data


def test_cargo_serializer_read_only_fields():
    """uuid e timestamps são read-only no create."""
    data = {
        "uuid": "invalid-uuid",
        "nome": "Novo Nome",
        "criado_em": "2024-01-01T00:00:00Z",
        "atualizado_em": "2024-01-01T00:00:00Z",
    }
    serializer = CargoSerializer(data=data)
    assert serializer.is_valid()
    cargo = serializer.save()
    assert cargo.nome == "Novo Nome"
    assert str(cargo.uuid) != "invalid-uuid"


def test_cargo_list_serializer_fields(cargo_analista):
    """List serializer é enxuto (sem timestamps)."""
    data = CargoListSerializer(cargo_analista).data
    assert set(data.keys()) >= {"uuid", "nome", "codigo"}
    assert "criado_em" not in data
    assert "atualizado_em" not in data


def test_cargo_select_serializer_fields(cargo_analista):
    """Select serializer usa value/label."""
    data = CargoSelectSerializer(cargo_analista).data
    assert data["value"] == str(cargo_analista.uuid)
    assert data["label"] == "Analista de Sistemas"
    assert "uuid" not in data
    assert "nome" not in data


def test_cargo_serializer_validation_valid(cargo_data):
    """Payload válido passa na validação."""
    assert CargoSerializer(data=cargo_data).is_valid()


def test_cargo_serializer_validation_empty_nome(cargo_data_invalid):
    """Nome vazio é rejeitado."""
    serializer = CargoSerializer(data=cargo_data_invalid)
    assert not serializer.is_valid()
    assert "nome" in serializer.errors


def test_cargo_serializer_validation_long_nome(cargo_data_long_name):
    """Nome acima do max_length é rejeitado."""
    serializer = CargoSerializer(data=cargo_data_long_name)
    assert not serializer.is_valid()
    assert "nome" in serializer.errors


def test_cargo_serializer_create(cargo_data):
    """Create via serializer persiste o cargo."""
    serializer = CargoSerializer(data=cargo_data)
    assert serializer.is_valid()
    cargo = serializer.save()
    assert cargo.nome == "Novo Cargo de Teste"
    assert cargo.uuid is not None


def test_cargo_serializer_update(cargo_analista):
    """Update parcial altera o nome."""
    serializer = CargoSerializer(
        cargo_analista, data={"nome": "Nome Atualizado"}, partial=True
    )
    assert serializer.is_valid()
    cargo = serializer.save()
    assert cargo.nome == "Nome Atualizado"
    assert cargo.uuid == cargo_analista.uuid


def test_cargo_serializer_com_codigo():
    """Serializer aceita e persiste codigo."""
    serializer = CargoSerializer(data={"nome": "Com Código", "codigo": 99})
    assert serializer.is_valid(), serializer.errors
    cargo = serializer.save()
    assert cargo.codigo == 99
