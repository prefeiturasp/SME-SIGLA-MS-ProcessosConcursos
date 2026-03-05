import pytest
from concursos.models import Cargo, AutorizacaoPublicada
from concursos.serializers import AutorizacaoPublicadaSerializer

pytestmark = pytest.mark.django_db


def test_autorizacao_publicada_serializer_fields():
    obj = AutorizacaoPublicada.objects.create()
    data = AutorizacaoPublicadaSerializer(obj).data
    for field in ['uuid', 'cargo', 'autorizacoes', 'data_autorizacao', 'observacao', 'criado_em', 'atualizado_em']:
        assert field in data


def test_autorizacao_publicada_create_with_valid_cargo():
    cargo = Cargo.objects.create(nome='Teste')
    payload = {
        'cargo': str(cargo.uuid),
        'autorizacoes': 3,
        'observacao': 'Obs',
    }
    serializer = AutorizacaoPublicadaSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors
    obj = serializer.save()
    assert obj.cargo == cargo
    assert obj.autorizacoes == 3
