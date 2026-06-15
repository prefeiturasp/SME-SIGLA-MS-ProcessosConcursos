from datetime import date

import pytest
from django.urls import reverse

from concursos.models import AutorizacaoPublicada, Cargo, Concurso

pytestmark = pytest.mark.django_db


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
