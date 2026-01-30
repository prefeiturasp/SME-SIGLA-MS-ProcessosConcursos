import pytest
from concursos.serializers import (
    CargoSerializer,
    CargoListSerializer,
    CargoSelectSerializer,
)

pytestmark = pytest.mark.django_db


def test_cargo_serializer_fields(cargo_analista):
    serializer = CargoSerializer(cargo_analista)
    data = serializer.data
    assert 'uuid' in data
    assert 'nome' in data
    assert 'criado_em' in data
    assert 'atualizado_em' in data
    assert data['nome'] == 'Analista de Sistemas'
    assert data['uuid'] == str(cargo_analista.uuid)


def test_cargo_serializer_read_only_fields():
    data = {
        'uuid': 'invalid-uuid',
        'nome': 'Novo Nome',
        'criado_em': '2024-01-01T00:00:00Z',
        'atualizado_em': '2024-01-01T00:00:00Z'
    }
    serializer = CargoSerializer(data=data)
    assert serializer.is_valid()
    cargo = serializer.save()
    assert cargo.nome == 'Novo Nome'
    assert str(cargo.uuid) != 'invalid-uuid'


def test_cargo_list_serializer_fields(cargo_analista):
    serializer = CargoListSerializer(cargo_analista)
    data = serializer.data
    assert 'uuid' in data
    assert 'nome' in data
    assert 'criado_em' not in data
    assert 'atualizado_em' not in data
    assert data['nome'] == 'Analista de Sistemas'
    assert data['uuid'] == str(cargo_analista.uuid)


def test_cargo_select_serializer_fields(cargo_analista):
    serializer = CargoSelectSerializer(cargo_analista)
    data = serializer.data
    assert 'value' in data
    assert 'label' in data
    assert 'uuid' not in data
    assert 'nome' not in data
    assert data['value'] == str(cargo_analista.uuid)
    assert data['label'] == 'Analista de Sistemas'


def test_cargo_serializer_validation_valid(cargo_data):
    serializer = CargoSerializer(data=cargo_data)
    assert serializer.is_valid()


def test_cargo_serializer_validation_empty_nome(cargo_data_invalid):
    serializer = CargoSerializer(data=cargo_data_invalid)
    assert not serializer.is_valid()
    assert 'nome' in serializer.errors


def test_cargo_serializer_validation_long_nome(cargo_data_long_name):
    serializer = CargoSerializer(data=cargo_data_long_name)
    assert not serializer.is_valid()
    assert 'nome' in serializer.errors


def test_cargo_serializer_create(cargo_data):
    serializer = CargoSerializer(data=cargo_data)
    assert serializer.is_valid()
    cargo = serializer.save()
    assert cargo.nome == 'Novo Cargo de Teste'
    assert cargo.uuid is not None
    assert cargo.criado_em is not None
    assert cargo.atualizado_em is not None


def test_cargo_serializer_update(cargo_analista):
    data = {'nome': 'Nome Atualizado'}
    serializer = CargoSerializer(cargo_analista, data=data, partial=True)
    assert serializer.is_valid()
    cargo = serializer.save()
    assert cargo.nome == 'Nome Atualizado'
    assert cargo.uuid == cargo_analista.uuid

