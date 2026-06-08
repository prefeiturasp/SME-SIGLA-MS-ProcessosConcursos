from datetime import date

import pytest
from django.urls import reverse

from concursos.models import AutorizacaoPublicada, Cargo, Concurso

pytestmark = pytest.mark.django_db


def test_total_autorizacoes_publicadas_por_ano(api_client):
    url = reverse("autorizacao-publicada-total")

    cargo_a = Cargo.objects.create(nome="Cargo A")
    cargo_b = Cargo.objects.create(nome="Cargo B")
    cargo_fora = Cargo.objects.create(nome="Cargo Fora")

    concurso = Concurso.objects.create(nome="Concurso X")
    concurso.cargos.add(cargo_a, cargo_b)

    # 2026: 100 + 50 = 150
    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=100, data_autorizacao=date(2026, 3, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_b, autorizacoes=50, data_autorizacao=date(2026, 7, 10)
    )
    # 2025: 80
    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=80, data_autorizacao=date(2025, 1, 5)
    )
    # cargo fora do concurso nao conta
    AutorizacaoPublicada.objects.create(
        cargo=cargo_fora, autorizacoes=999, data_autorizacao=date(2026, 1, 1)
    )
    # data nula e ignorada
    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=7, data_autorizacao=None
    )

    resp = api_client.post(
        url, {"concurso_uuid": str(concurso.uuid)}, format="json"
    )

    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data["2026"] == {"autorizacoes-publicadas": 150}
    assert data["2025"] == {"autorizacoes-publicadas": 80}


def test_total_autorizacoes_exige_concurso_uuid(api_client):
    url = reverse("autorizacao-publicada-total")
    resp = api_client.post(url, {}, format="json")
    assert resp.status_code == 400


def test_total_autorizacoes_filtra_por_anos(api_client):
    url = reverse("autorizacao-publicada-total")

    cargo = Cargo.objects.create(nome="Cargo A")
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
        "2026": {"autorizacoes-publicadas": 100},
        "2025": {"autorizacoes-publicadas": 80},
    }
    assert "2024" not in data


def test_total_autorizacoes_sem_anos_retorna_todos(api_client):
    url = reverse("autorizacao-publicada-total")

    cargo = Cargo.objects.create(nome="Cargo A")
    concurso = Concurso.objects.create(nome="Concurso X")
    concurso.cargos.add(cargo)

    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=100, data_autorizacao=date(2026, 3, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=30, data_autorizacao=date(2024, 1, 5)
    )

    resp = api_client.post(
        url, {"concurso_uuid": str(concurso.uuid)}, format="json"
    )

    assert resp.status_code == 200, resp.content
    data = resp.json()
    assert data == {
        "2026": {"autorizacoes-publicadas": 100},
        "2024": {"autorizacoes-publicadas": 30},
    }
