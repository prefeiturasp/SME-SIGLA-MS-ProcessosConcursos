import pytest
from concursos.models import Cargo, AutorizacaoPublicada
from concursos.serializers import AutorizacaoPublicadaSerializer

pytestmark = pytest.mark.django_db


def test_autorizacao_publicada_serializer_fields():
    obj = AutorizacaoPublicada.objects.create()
    data = AutorizacaoPublicadaSerializer(obj).data
    for field in ['uuid', 'cargo', 'vagas_sem_efeito', 'autorizacoes', 'autorizacoes_sem_efeito', 'data_autorizacao', 'observacao', 'criado_em', 'atualizado_em']:
        assert field in data


def test_autorizacao_publicada_create_with_valid_cargo():
    cargo = Cargo.objects.create(nome='Teste')
    payload = {
        'cargo': str(cargo.uuid),
        'vagas_sem_efeito': False,
        'autorizacoes': 3,
        'autorizacoes_sem_efeito': 1,
        'observacao': 'Obs',
    }
    serializer = AutorizacaoPublicadaSerializer(data=payload)
    assert serializer.is_valid(), serializer.errors
    obj = serializer.save()
    assert obj.cargo == cargo
    assert obj.autorizacoes == 3
    assert obj.autorizacoes_sem_efeito == 1
