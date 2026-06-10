"""Módulo tests/views/test_cargos_view."""

from datetime import date
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from concursos.models import AutorizacaoPublicada, Cargo

pytestmark = pytest.mark.django_db


def test_list_cargos_success(authenticated_client, cargos):
    """Verifica list cargos success."""
    url = reverse("cargo-list")
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 3
    cargos_data = response.data["results"]
    cargo_nomes = [cargo["nome"] for cargo in cargos_data]
    assert all("codigo" in cargo for cargo in cargos_data)
    assert "Analista de Sistemas" in cargo_nomes
    assert "Desenvolvedor Backend" in cargo_nomes
    assert "Professor de Matemática" in cargo_nomes


def test_create_cargo_success(authenticated_client, cargo_data):
    """Verifica create cargo success."""
    url = reverse("cargo-list")
    response = authenticated_client.post(url, {**cargo_data, "codigo": "1234"})
    assert response.status_code == status.HTTP_201_CREATED
    assert Cargo.objects.count() == 1
    novo_cargo = Cargo.objects.get(nome="Novo Cargo de Teste")
    assert novo_cargo.uuid is not None
    assert novo_cargo.criado_em is not None
    assert novo_cargo.atualizado_em is not None
    assert novo_cargo.codigo == 1234


def test_retrieve_cargo_success(authenticated_client, cargo_analista):
    """Verifica retrieve cargo success."""
    url = reverse("cargo-detail", kwargs={"pk": cargo_analista.uuid})
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Analista de Sistemas"
    assert response.data["uuid"] == str(cargo_analista.uuid)


def test_retrieve_cargo_not_found(authenticated_client, fake_uuid):
    """Verifica retrieve cargo not found."""
    url = reverse("cargo-detail", kwargs={"pk": fake_uuid})
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_cargo_success(authenticated_client, cargo_analista):
    """Verifica update cargo success."""
    url = reverse("cargo-detail", kwargs={"pk": cargo_analista.uuid})
    data = {"nome": "Analista de Sistemas Atualizado"}
    response = authenticated_client.put(url, data)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Analista de Sistemas Atualizado"
    cargo_analista.refresh_from_db()
    assert cargo_analista.nome == "Analista de Sistemas Atualizado"


def test_delete_cargo_success(authenticated_client, cargo_analista):
    """Verifica delete cargo success."""
    url = reverse("cargo-detail", kwargs={"pk": cargo_analista.uuid})
    response = authenticated_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Cargo.objects.count() == 0
    with pytest.raises(Cargo.DoesNotExist):
        Cargo.objects.get(uuid=cargo_analista.uuid)


def test_autorizacoes_publicadas_agrupa_e_integra_ms_escolhas(
    authenticated_client,
):
    """Testa a action /cargos/autorizacoes-publicadas/ agregando dados."""
    cargo_a = Cargo.objects.create(nome="Cargo A", codigo=1001)
    cargo_b = Cargo.objects.create(nome="Cargo B", codigo=1002)
    # cria autorizações publicadas locais
    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=2, data_autorizacao=date(2026, 1, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=1, data_autorizacao=date(2026, 1, 15)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_b, autorizacoes=5, data_autorizacao=date(2025, 12, 31)
    )

    # mock do serviço externo retornando totais de escolhas por cargo
    payload = {"1001": 3, "1002": 1}

    class DummyResp:
        """Define DummyResp."""

        def json(self):
            """Executa json."""
            return payload

    with patch(
        "concursos.views.cargos.EscolhasAPIService.get_escolhas_por_cargo",
        return_value=DummyResp(),
    ):
        url = reverse("cargo-autorizacoes-publicadas")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        assert isinstance(resp.data, list)
        # transforma resposta em mapa por codigo para facilitar asserts
        by_codigo = {item["codigo"]: item for item in resp.data}
        assert 1001 in by_codigo and 1002 in by_codigo

        a = by_codigo[1001]
        b = by_codigo[1002]
        # verifica totais de escolhas vindos do serviço externo
        assert a["total_escolhas"] == payload["1001"]
        assert b["total_escolhas"] == payload["1002"]
        # verifica agregações locais (somas)
        assert a["autorizacoes"] == 3  # 2 + 1
        assert a["data_autorizacao_mais_recente"] == "2026-01-15"
        assert b["autorizacoes"] == 5
        assert b["data_autorizacao_mais_recente"] == "2025-12-31"
