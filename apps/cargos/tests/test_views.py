"""Testes unitários das views de cargos."""

from datetime import date
from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework import status

from autorizacoes.models import AutorizacaoPublicada
from cargos.models import Cargo

pytestmark = pytest.mark.django_db


def test_list_cargos_success(authenticated_client, cargos):
    """Lista cargos retorna os três fixtures."""
    url = reverse("cargo-list")
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    cargos_data = (
        response.data["results"]
        if "results" in response.data
        else response.data
    )
    assert len(cargos_data) == 3
    cargo_nomes = [cargo["nome"] for cargo in cargos_data]
    assert all("codigo" in cargo for cargo in cargos_data)
    assert "Analista de Sistemas" in cargo_nomes
    assert "Desenvolvedor Backend" in cargo_nomes
    assert "Professor de Matemática" in cargo_nomes


def test_create_cargo_success(authenticated_client, cargo_data):
    """POST cria cargo com codigo."""
    url = reverse("cargo-list")
    response = authenticated_client.post(url, {**cargo_data, "codigo": "1234"})
    assert response.status_code == status.HTTP_201_CREATED
    assert Cargo.objects.count() == 1
    novo_cargo = Cargo.objects.get(nome="Novo Cargo de Teste")
    assert novo_cargo.codigo == 1234


def test_retrieve_cargo_success(authenticated_client, cargo_analista):
    """GET detail retorna o cargo."""
    url = reverse("cargo-detail", kwargs={"pk": cargo_analista.uuid})
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["nome"] == "Analista de Sistemas"


def test_retrieve_cargo_not_found(authenticated_client, fake_uuid):
    """GET detail com UUID inexistente retorna 404."""
    url = reverse("cargo-detail", kwargs={"pk": fake_uuid})
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_cargo_success(authenticated_client, cargo_analista):
    """PUT atualiza o nome do cargo."""
    url = reverse("cargo-detail", kwargs={"pk": cargo_analista.uuid})
    response = authenticated_client.put(
        url, {"nome": "Analista de Sistemas Atualizado"}
    )
    assert response.status_code == status.HTTP_200_OK
    cargo_analista.refresh_from_db()
    assert cargo_analista.nome == "Analista de Sistemas Atualizado"


def test_delete_cargo_success(authenticated_client, cargo_analista):
    """DELETE remove o cargo."""
    url = reverse("cargo-detail", kwargs={"pk": cargo_analista.uuid})
    response = authenticated_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Cargo.objects.count() == 0


@pytest.mark.skip(reason="Config do settings com erro inesperado")
def test_autorizacoes_publicadas_agrupa_e_integra_ms_escolhas(
    authenticated_client,
):
    """Action autorizacoes-publicadas agrega locais + MS-Escolhas."""
    cargo_a = Cargo.objects.create(nome="Cargo A", codigo=1001)
    cargo_b = Cargo.objects.create(nome="Cargo B", codigo=1002)
    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=2, data_autorizacao=date(2026, 1, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_a, autorizacoes=1, data_autorizacao=date(2026, 1, 15)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo_b, autorizacoes=5, data_autorizacao=date(2025, 12, 31)
    )

    payload = {"1001": 3, "1002": 1}

    class DummyResp:
        def json(self):
            return payload

    with patch(
        "cargos.services.cargos_service.EscolhasAPIService.get_escolhas_por_cargo",
        return_value=DummyResp(),
    ):
        url = reverse("cargo-autorizacoes-publicadas")
        resp = authenticated_client.get(url)
        assert resp.status_code == status.HTTP_200_OK
        by_codigo = {item["codigo"]: item for item in resp.data}
        assert by_codigo[1001]["total_escolhas"] == 3
        assert by_codigo[1001]["autorizacoes"] == 3
        assert by_codigo[1001]["data_autorizacao_mais_recente"] == "2026-01-15"
        assert by_codigo[1002]["autorizacoes"] == 5


def test_busca_cargo_por_codigo_parcial(authenticated_client):
    """Search casa cargos pelo codigo (match parcial)."""
    Cargo.objects.create(nome="PROF.ED.INF.I-MAT", codigo=4123)
    Cargo.objects.create(nome="PROF.ED.INF.I-HIS", codigo=4124)
    Cargo.objects.create(nome="Outro Cargo", codigo=9999)

    url = reverse("cargo-list")
    response = authenticated_client.get(url, {"search": "412"})
    assert response.status_code == status.HTTP_200_OK
    dados = (
        response.data["results"]
        if "results" in response.data
        else response.data
    )
    nomes = [c["nome"] for c in dados]
    assert "PROF.ED.INF.I-MAT" in nomes
    assert "PROF.ED.INF.I-HIS" in nomes
    assert "Outro Cargo" not in nomes


def test_busca_cargo_por_nome_ainda_funciona(authenticated_client):
    """Search por nome continua funcionando."""
    Cargo.objects.create(nome="Analista Judiciario", codigo=100)
    Cargo.objects.create(nome="Tecnico", codigo=200)

    url = reverse("cargo-list")
    response = authenticated_client.get(url, {"search": "Analista"})
    assert response.status_code == status.HTTP_200_OK
    dados = (
        response.data["results"]
        if "results" in response.data
        else response.data
    )
    nomes = [c["nome"] for c in dados]
    assert "Analista Judiciario" in nomes
    assert "Tecnico" not in nomes
