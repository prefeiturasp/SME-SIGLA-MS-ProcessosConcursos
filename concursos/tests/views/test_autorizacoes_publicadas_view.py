import pytest
from django.urls import reverse
from rest_framework import status
from concursos.models import Cargo, AutorizacaoPublicada

pytestmark = pytest.mark.django_db


def criar_autorizacao(cargo: Cargo | None = None, **kwargs) -> AutorizacaoPublicada:
    defaults = dict(
        vagas_sem_efeito=False,
        autorizacoes=2,
        autorizacoes_sem_efeito=1,
        observacao='Obs teste',
    )
    defaults.update(kwargs)
    return AutorizacaoPublicada.objects.create(cargo=cargo, **defaults)


def test_list_autorizacoes_publicadas_success(api_client):
    cargo_a = Cargo.objects.create(nome='Cargo A')
    cargo_b = Cargo.objects.create(nome='Cargo B')
    criar_autorizacao(cargo_a, autorizacoes=3)
    criar_autorizacao(cargo_b, autorizacoes=1)

    url = reverse('autorizacao-publicada-list')
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    # paginado: espera 'results'
    assert 'results' in resp.data
    assert resp.data['count'] == 2
    assert len(resp.data['results']) == 2


def test_list_autorizacoes_publicadas_filter_by_cargo_codigo(api_client):
    cargo_a = Cargo.objects.create(nome='Cargo A', codigo=1001)
    cargo_b = Cargo.objects.create(nome='Cargo B', codigo=1002)
    criar_autorizacao(cargo_a)
    criar_autorizacao(cargo_b)

    url = reverse('autorizacao-publicada-list')
    resp = api_client.get(url, {'cargo__codigo': 1001})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['count'] == 1
    item = resp.data['results'][0]
    # serializer expõe 'cargo' como UUID (write field), aqui voltará UUID ou null conforme implementação;
    # validamos campos básicos para garantir resposta
    assert 'uuid' in item
    assert 'autorizacoes' in item


def test_retrieve_autorizacao_publicada_success(api_client):
    cargo = Cargo.objects.create(nome='Cargo A')
    obj = criar_autorizacao(cargo)

    url = reverse('autorizacao-publicada-detail', kwargs={'pk': obj.uuid})
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data['uuid'] == str(obj.uuid)
    assert 'autorizacoes' in resp.data


def test_create_autorizacao_publicada_success_with_cargo(api_client):
    cargo = Cargo.objects.create(nome='Cargo X')
    url = reverse('autorizacao-publicada-list')
    payload = {
        'cargo': str(cargo.uuid),
        'vagas_sem_efeito': True,
        'autorizacoes': 5,
        'autorizacoes_sem_efeito': 0,
        'data_autorizacao': '2026-01-29',
        'observacao': 'Criado via teste',
    }
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == status.HTTP_201_CREATED
    created = AutorizacaoPublicada.objects.get(uuid=resp.data['uuid'])
    assert created.cargo == cargo
    assert created.autorizacoes == 5
    assert created.vagas_sem_efeito is True


def test_create_autorizacao_publicada_invalid_cargo(api_client):
    url = reverse('autorizacao-publicada-list')
    payload = {
        'cargo': '00000000-0000-0000-0000-000000000000',
        'autorizacoes': 1,
    }
    resp = api_client.post(url, payload, format='json')
    # A validação falha durante o create() ao resolver o cargo
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert 'cargo' in resp.data


def test_patch_autorizacao_publicada_success(api_client):
    obj = criar_autorizacao(None, autorizacoes=2, autorizacoes_sem_efeito=1, observacao='old')
    url = reverse('autorizacao-publicada-detail', kwargs={'pk': obj.uuid})
    payload = {
        'vagas_sem_efeito': True,
        'autorizacoes': 7,
        'autorizacoes_sem_efeito': 3,
        'data_autorizacao': '2026-01-29',
        'observacao': 'nova',
    }
    resp = api_client.patch(url, payload, format='json')
    assert resp.status_code == status.HTTP_200_OK
    obj.refresh_from_db()
    assert obj.vagas_sem_efeito is True
    assert obj.autorizacoes == 7
    assert obj.autorizacoes_sem_efeito == 3
    assert str(obj.data_autorizacao) == '2026-01-29'
    assert obj.observacao == 'nova'


def test_delete_autorizacao_publicada_success(api_client):
    obj = criar_autorizacao()
    url = reverse('autorizacao-publicada-detail', kwargs={'pk': obj.uuid})
    resp = api_client.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert AutorizacaoPublicada.objects.filter(uuid=obj.uuid).count() == 0

