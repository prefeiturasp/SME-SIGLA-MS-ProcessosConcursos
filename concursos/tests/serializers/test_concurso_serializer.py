"""Módulo tests/serializers/test_concurso_serializer."""

import pytest

from concursos.serializers import (
    ConcursoListSerializer,
    ConcursoSelectSerializer,
    ConcursoSerializer,
)

pytestmark = pytest.mark.django_db


def test_concurso_serializer_fields(concurso_analista):
    """Verifica concurso serializer fields."""
    serializer = ConcursoSerializer(concurso_analista)
    data = serializer.data
    assert "uuid" in data
    assert "nome" in data
    assert "cargos" in data
    assert "criado_em" in data
    assert "atualizado_em" in data
    assert data["nome"] == "Concurso de Analista"
    assert data["uuid"] == str(concurso_analista.uuid)
    assert len(data["cargos"]) == 1
    assert data["cargos"][0]["nome"] == "Analista de Sistemas"


def test_concurso_serializer_create(concurso_data):
    """Verifica concurso serializer create."""
    serializer = ConcursoSerializer(data=concurso_data)
    assert serializer.is_valid()
    concurso = serializer.save()
    assert concurso.nome == "Novo Concurso de Teste"
    assert concurso.cargos.count() == 1


def test_concurso_serializer_create_without_cargos(concurso_data_no_cargos):
    """Verifica concurso serializer create without cargos."""
    serializer = ConcursoSerializer(data=concurso_data_no_cargos)
    assert serializer.is_valid()
    concurso = serializer.save()
    assert concurso.nome == "Concurso Sem Cargos"
    assert concurso.cargos.count() == 0


def test_concurso_serializer_create_with_invalid_cargo_ids(
    concurso_data_invalid_cargo_ids,
):
    """Verifica concurso serializer create with invalid cargo ids."""
    serializer = ConcursoSerializer(data=concurso_data_invalid_cargo_ids)
    assert serializer.is_valid()
    concurso = serializer.save()
    assert concurso.nome == "Concurso com Cargo Inválido"
    assert concurso.cargos.count() == 0


def test_concurso_serializer_create_with_multiple_cargos(
    concurso_data_multiple_cargos,
):
    """Verifica concurso serializer create with multiple cargos."""
    serializer = ConcursoSerializer(data=concurso_data_multiple_cargos)
    assert serializer.is_valid()
    concurso = serializer.save()
    assert concurso.nome == "Concurso com Múltiplos Cargos"
    assert concurso.cargos.count() == 2


def test_concurso_serializer_update(concurso_analista, cargo_desenvolvedor):
    """Verifica concurso serializer update."""
    data = {
        "nome": "Concurso Atualizado",
        "cargos_ids": [str(cargo_desenvolvedor.uuid)],
    }
    serializer = ConcursoSerializer(concurso_analista, data=data, partial=True)
    assert serializer.is_valid()
    concurso = serializer.save()
    assert concurso.nome == "Concurso Atualizado"
    assert concurso.cargos.count() == 1
    assert cargo_desenvolvedor in concurso.cargos.all()


def test_concurso_serializer_update_clear_cargos(concurso_analista):
    """Verifica concurso serializer update clear cargos."""
    data = {"cargos_ids": []}
    serializer = ConcursoSerializer(concurso_analista, data=data, partial=True)
    assert serializer.is_valid()
    concurso = serializer.save()
    assert concurso.cargos.count() == 0


def test_concurso_serializer_validation_valid(concurso_data):
    """Verifica concurso serializer validation valid."""
    serializer = ConcursoSerializer(data=concurso_data)
    assert serializer.is_valid()


def test_concurso_serializer_validation_empty_nome(concurso_data_invalid):
    """Verifica concurso serializer validation empty nome."""
    serializer = ConcursoSerializer(data=concurso_data_invalid)
    assert not serializer.is_valid()
    assert "nome" in serializer.errors


def test_concurso_serializer_validation_long_nome():
    """Verifica concurso serializer validation long nome."""
    data = {"nome": "A" * 201}
    serializer = ConcursoSerializer(data=data)
    assert not serializer.is_valid()
    assert "nome" in serializer.errors


def test_concurso_list_serializer_fields(concurso_analista):
    """Verifica concurso list serializer fields."""
    serializer = ConcursoListSerializer(concurso_analista)
    data = serializer.data
    assert "uuid" in data
    assert "nome" in data
    assert "cargos" in data
    assert "criado_em" not in data
    assert "atualizado_em" not in data
    assert data["nome"] == "Concurso de Analista"
    assert data["uuid"] == str(concurso_analista.uuid)
    assert len(data["cargos"]) == 1


def test_concurso_select_serializer_fields(concurso_analista):
    """Verifica concurso select serializer fields."""
    serializer = ConcursoSelectSerializer(concurso_analista)
    data = serializer.data
    assert "value" in data
    assert "label" in data
    assert "cargos" in data
    assert "uuid" not in data
    assert "nome" not in data
    assert data["value"] == str(concurso_analista.uuid)
    assert data["label"] == "Concurso de Analista"
    assert len(data["cargos"]) == 1


def test_concurso_serializer_cargos_ids_field(concurso_analista):
    """Verifica concurso serializer cargos ids field."""
    serializer = ConcursoSerializer(concurso_analista)
    data = serializer.data
    assert "cargos_ids" not in data
    data = {
        "nome": "Teste",
        "cargos_ids": [str(concurso_analista.cargos.first().uuid)],
    }
    serializer = ConcursoSerializer(data=data)
    assert serializer.is_valid()


def test_concurso_serializer_nested_cargos(
    concurso_analista, cargo_desenvolvedor
):
    """Verifica concurso serializer nested cargos."""
    concurso_analista.cargos.add(cargo_desenvolvedor)
    serializer = ConcursoSerializer(concurso_analista)
    data = serializer.data
    assert len(data["cargos"]) == 2
    cargo_nomes = [cargo["nome"] for cargo in data["cargos"]]
    assert "Analista de Sistemas" in cargo_nomes
    assert "Desenvolvedor Backend" in cargo_nomes


def test_concurso_serializer_partial_update(concurso_analista):
    """Verifica concurso serializer partial update."""
    data = {"nome": "Nome Atualizado"}
    serializer = ConcursoSerializer(concurso_analista, data=data, partial=True)
    assert serializer.is_valid()
    concurso = serializer.save()
    assert concurso.nome == "Nome Atualizado"
    assert concurso.cargos.count() == 1


def test_concurso_serializer_create_with_empty_cargos_ids():
    """Verifica concurso serializer create with empty cargos ids."""
    data = {"nome": "Concurso Vazio", "cargos_ids": []}
    serializer = ConcursoSerializer(data=data)
    assert serializer.is_valid()
    concurso = serializer.save()
    assert concurso.nome == "Concurso Vazio"
    assert concurso.cargos.count() == 0


def test_concurso_serializer_update_with_none_cargos_ids(concurso_analista):
    """Verifica concurso serializer update with none cargos ids."""
    data = {"nome": "Nome Atualizado"}
    serializer = ConcursoSerializer(concurso_analista, data=data, partial=True)
    assert serializer.is_valid()
    concurso = serializer.save()
    assert concurso.nome == "Nome Atualizado"
    assert concurso.cargos.count() == 1


def test_concurso_serializer_invalid_uuid_format():
    """Verifica concurso serializer invalid uuid format."""
    data = {"nome": "Concurso Teste", "cargos_ids": ["invalid-uuid-format"]}
    serializer = ConcursoSerializer(data=data)
    assert not serializer.is_valid()
    assert "cargos_ids" in serializer.errors


def test_concurso_serializer_mixed_valid_invalid_cargos(cargo_analista):
    """Verifica concurso serializer mixed valid invalid cargos."""
    import uuid

    fake_uuid = uuid.uuid4()
    data = {
        "nome": "Concurso Misto",
        "cargos_ids": [str(cargo_analista.uuid), str(fake_uuid)],
    }
    serializer = ConcursoSerializer(data=data)
    assert serializer.is_valid()
    concurso = serializer.save()
    assert concurso.nome == "Concurso Misto"
    assert concurso.cargos.count() == 1
    assert cargo_analista in concurso.cargos.all()
