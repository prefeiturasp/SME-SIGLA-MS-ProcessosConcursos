"""Testes unitários das views de autorizações publicadas e extracão de dados."""

from datetime import date

import pytest
from django.urls import reverse
from rest_framework import status

from autorizacoes.models import AutorizacaoPublicada
from cargos.models import Cargo
from concursos.models import Concurso

pytestmark = pytest.mark.django_db


def criar_autorizacao(
    cargo: Cargo | None = None, **kwargs
) -> AutorizacaoPublicada:
    """Cria autorização para testes."""
    defaults = dict(
        autorizacoes=2,
        observacao="Obs teste",
    )
    defaults.update(kwargs)
    return AutorizacaoPublicada.objects.create(cargo=cargo, **defaults)

def test_list_autorizacoes_publicadas_success(api_client):
    """Verifica list autorizacoes publicadas success."""
    cargo_a = Cargo.objects.create(nome="Cargo A")
    cargo_b = Cargo.objects.create(nome="Cargo B")
    criar_autorizacao(cargo_a, autorizacoes=3)
    criar_autorizacao(cargo_b, autorizacoes=1)

    url = reverse("autorizacao-publicada-list")
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    # paginado: espera 'results'
    assert "results" in resp.data
    assert resp.data["count"] == 2
    assert len(resp.data["results"]) == 2


def test_list_autorizacoes_publicadas_filter_by_cargo_codigo(api_client):
    """Verifica list autorizacoes publicadas filter by cargo codigo."""
    cargo_a = Cargo.objects.create(nome="Cargo A", codigo=1001)
    cargo_b = Cargo.objects.create(nome="Cargo B", codigo=1002)
    criar_autorizacao(cargo_a)
    criar_autorizacao(cargo_b)

    url = reverse("autorizacao-publicada-list")
    resp = api_client.get(url, {"cargo__codigo": 1001})
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["count"] == 1
    item = resp.data["results"][0]
    # serializer expõe 'cargo' como UUID (write field); voltará UUID
    # ou null conforme implementação. Validamos campos básicos.
    assert "uuid" in item
    assert "autorizacoes" in item


def test_retrieve_autorizacao_publicada_success(api_client):
    """Verifica retrieve autorizacao publicada success."""
    cargo = Cargo.objects.create(nome="Cargo A")
    obj = criar_autorizacao(cargo)

    url = reverse("autorizacao-publicada-detail", kwargs={"pk": obj.uuid})
    resp = api_client.get(url)
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data["uuid"] == str(obj.uuid)
    assert "autorizacoes" in resp.data


def test_create_autorizacao_publicada_success_with_cargo(api_client):
    """Verifica create autorizacao publicada success with cargo."""
    cargo = Cargo.objects.create(nome="Cargo X")
    url = reverse("autorizacao-publicada-list")
    payload = {
        "cargo": str(cargo.uuid),
        "autorizacoes": 5,
        "data_autorizacao": "2026-01-29",
        "observacao": "Criado via teste",
    }
    resp = api_client.post(url, payload, format="json")
    assert resp.status_code == status.HTTP_201_CREATED
    created = AutorizacaoPublicada.objects.get(uuid=resp.data["uuid"])
    assert created.cargo == cargo
    assert created.autorizacoes == 5


def test_create_autorizacao_publicada_invalid_cargo(api_client):
    """Verifica create autorizacao publicada invalid cargo."""
    url = reverse("autorizacao-publicada-list")
    payload = {
        "cargo": "00000000-0000-0000-0000-000000000000",
        "autorizacoes": 1,
    }
    resp = api_client.post(url, payload, format="json")
    # A validação falha durante o create() ao resolver o cargo
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "cargo" in resp.data


def test_patch_autorizacao_publicada_success(api_client):
    """Verifica patch autorizacao publicada success."""
    obj = criar_autorizacao(None, autorizacoes=2, observacao="old")
    url = reverse("autorizacao-publicada-detail", kwargs={"pk": obj.uuid})
    payload = {
        "autorizacoes": 7,
        "data_autorizacao": "2026-01-29",
        "observacao": "nova",
    }
    resp = api_client.patch(url, payload, format="json")
    assert resp.status_code == status.HTTP_200_OK
    obj.refresh_from_db()
    assert obj.autorizacoes == 7
    assert str(obj.data_autorizacao) == "2026-01-29"
    assert obj.observacao == "nova"


def test_delete_autorizacao_publicada_success(api_client):
    """Verifica delete autorizacao publicada success."""
    obj = criar_autorizacao()
    url = reverse("autorizacao-publicada-detail", kwargs={"pk": obj.uuid})
    resp = api_client.delete(url)
    assert resp.status_code == status.HTTP_204_NO_CONTENT
    assert AutorizacaoPublicada.objects.filter(uuid=obj.uuid).count() == 0

def test_total_autorizacoes_publicadas_por_ano(api_client):
    url = reverse("extracao-dados-list")

    cargo_a = Cargo.objects.create(nome="Cargo A", codigo=101)
    cargo_b = Cargo.objects.create(nome="Cargo B", codigo=102)
    cargo_fora = Cargo.objects.create(nome="Cargo Fora", codigo=999)

    concurso = Concurso.objects.create(nome="Concurso X")
    concurso.cargos.add(cargo_a, cargo_b)

    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=100, data_autorizacao=date(2026, 3, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_b, autorizacoes=50, data_autorizacao=date(2026, 7, 10)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=80, data_autorizacao=date(2025, 1, 5)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_fora, autorizacoes=999, data_autorizacao=date(2026, 1, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=7, data_autorizacao=None
    )

    resp = api_client.post(
        url,
        {"concurso_uuid": str(concurso.uuid), "anos": [2026, 2025]},
        format="json",
    )

    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data["2026"]["autorizacoes-publicadas"] == 150
    assert data["2025"]["autorizacoes-publicadas"] == 80
    assert data["2026"]["cargos"] == [
        {
            "uuid": str(cargo_a.uuid),
            "nome": "Cargo A",
            "codigo": 101,
            "autorizacoes": 100,
            "data_autorizacao": "2026-03-01",
        },
        {
            "uuid": str(cargo_b.uuid),
            "nome": "Cargo B",
            "codigo": 102,
            "autorizacoes": 50,
            "data_autorizacao": "2026-07-10",
        },
    ]
    assert data["2025"]["cargos"] == [
        {
            "uuid": str(cargo_a.uuid),
            "nome": "Cargo A",
            "codigo": 101,
            "autorizacoes": 80,
            "data_autorizacao": "2025-01-05",
        },
    ]


def test_total_sem_concurso_agrega_todos(api_client):
    url = reverse("extracao-dados-list")

    cargo_a = Cargo.objects.create(nome="Cargo A", codigo=101)
    cargo_b = Cargo.objects.create(nome="Cargo B", codigo=102)
    cargo_fora = Cargo.objects.create(nome="Cargo Fora", codigo=999)

    concurso_x = Concurso.objects.create(nome="Concurso X")
    concurso_x.cargos.add(cargo_a)
    concurso_y = Concurso.objects.create(nome="Concurso Y")
    concurso_y.cargos.add(cargo_b)

    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=100, data_autorizacao=date(2026, 3, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_b, autorizacoes=50, data_autorizacao=date(2025, 1, 5)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_fora, autorizacoes=999, data_autorizacao=date(2024, 1, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=7, data_autorizacao=None
    )

    resp = api_client.post(url, {}, format="json")

    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data["autorizacoes-publicadas"] == 1149
    assert data["cargos"] == [
        {
            "uuid": str(cargo_a.uuid),
            "nome": "Cargo A",
            "codigo": 101,
            "autorizacoes": 100,
            "data_autorizacao": "2026-03-01",
        },
        {
            "uuid": str(cargo_b.uuid),
            "nome": "Cargo B",
            "codigo": 102,
            "autorizacoes": 50,
            "data_autorizacao": "2025-01-05",
        },
        {
            "uuid": str(cargo_fora.uuid),
            "nome": "Cargo Fora",
            "codigo": 999,
            "autorizacoes": 999,
            "data_autorizacao": "2024-01-01",
        },
    ]


def test_total_autorizacoes_filtra_por_anos(api_client):
    url = reverse("extracao-dados-list")

    cargo = Cargo.objects.create(nome="Cargo A", codigo=101)
    concurso = Concurso.objects.create(nome="Concurso X")
    concurso.cargos.add(cargo)

    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=100, data_autorizacao=date(2026, 3, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=80, data_autorizacao=date(2025, 1, 5)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=30, data_autorizacao=date(2024, 1, 5)
    )

    resp = api_client.post(
        url,
        {"concurso_uuid": str(concurso.uuid), "anos": [2026, 2025]},
        format="json",
    )

    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data == {
        "2026": {
            "autorizacoes-publicadas": 100,
            "cargos": [
                {
                    "uuid": str(cargo.uuid),
                    "nome": "Cargo A",
                    "codigo": 101,
                    "autorizacoes": 100,
                    "data_autorizacao": "2026-03-01",
                },
            ],
        },
        "2025": {
            "autorizacoes-publicadas": 80,
            "cargos": [
                {
                    "uuid": str(cargo.uuid),
                    "nome": "Cargo A",
                    "codigo": 101,
                    "autorizacoes": 80,
                    "data_autorizacao": "2025-01-05",
                },
            ],
        },
    }
    assert "2024" not in data


def test_total_sem_anos_retorna_total(api_client):
    url = reverse("extracao-dados-list")

    cargo = Cargo.objects.create(nome="Cargo A", codigo=101)
    concurso = Concurso.objects.create(nome="Concurso X")
    concurso.cargos.add(cargo)

    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=100, data_autorizacao=date(2026, 3, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=30, data_autorizacao=date(2024, 1, 5)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=5, data_autorizacao=None
    )

    resp = api_client.post(
        url, {"concurso_uuid": str(concurso.uuid)}, format="json"
    )

    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data == {
        "autorizacoes-publicadas": 130,
        "cargos": [
            {
                "uuid": str(cargo.uuid),
                "nome": "Cargo A",
                "codigo": 101,
                "autorizacoes": 130,
                "data_autorizacao": "2026-03-01",
            },
        ],
    }


def test_data_autorizacao_mais_recente_por_cargo_com_multiplos_registros(
    api_client,
):
    url = reverse("extracao-dados-list")

    cargo = Cargo.objects.create(nome="Cargo A", codigo=101)
    concurso = Concurso.objects.create(nome="Concurso X")
    concurso.cargos.add(cargo)

    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=40, data_autorizacao=date(2026, 1, 10)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=60, data_autorizacao=date(2026, 8, 20)
    )

    resp = api_client.post(
        url,
        {"concurso_uuid": str(concurso.uuid), "anos": [2026]},
        format="json",
    )

    assert resp.status_code == 200, resp.content
    cargo_data = resp.json()["2026"]["cargos"][0]
    assert cargo_data["autorizacoes"] == 100
    assert cargo_data["data_autorizacao"] == "2026-08-20"
