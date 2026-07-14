"""Testes unitários dos services e repository de cargos."""

from datetime import date
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest
import requests
from django.conf import settings

from autorizacoes.models import AutorizacaoPublicada
from cargos.models import Cargo
from cargos.repository import CargoRepository
from cargos.services import CargosService, EscolhasAPIService

pytestmark = pytest.mark.django_db


# --- EscolhasAPIService ---


def test_get_escolhas_por_cargo_success():
    """Cliente chama o endpoint de agrupamento por cargo."""
    service = EscolhasAPIService(
        base_url="http://example.com", timeout_seconds=5
    )
    fake_response = Mock()
    fake_response.json.return_value = {"1001": 5, "1002": 4}
    fake_response.raise_for_status.return_value = None
    with patch(
        "cargos.services.escolhas_api_service.requests.get",
        return_value=fake_response,
    ) as mocked_get:
        resp = service.get_escolhas_por_cargo(headers={"X-Test": "1"})
        assert resp is fake_response
        mocked_get.assert_called_once_with(
            "http://example.com/api/v1/escolhas/agrupar-por-cargo/",
            headers={"Accept": "application/json", "X-Test": "1"},
            timeout=5,
        )
        assert resp.json() == {"1001": 5, "1002": 4}


def test_get_escolhas_por_cargo_http_error_propagates():
    """Erro HTTP do MS-Escolhas é propagado."""
    service = EscolhasAPIService(base_url="http://example.com")
    fake_response = Mock()
    fake_response.raise_for_status.side_effect = requests.HTTPError("boom")
    with (
        patch(
            "cargos.services.escolhas_api_service.requests.get",
            return_value=fake_response,
        ),
        pytest.raises(requests.HTTPError),
    ):
        service.get_escolhas_por_cargo()


def test_init_without_setting_and_without_base_url_raises(monkeypatch):
    """Sem ESCOLHAS_API_URL o serviço falha na criação."""
    monkeypatch.setattr(settings, "ESCOLHAS_API_URL", "", raising=False)
    with pytest.raises(ValueError):
        EscolhasAPIService()


# --- CargosService ---


def test_listar_autorizacoes_publicadas_agregadas_combina_escolhas():
    """Service agrega autorizações locais e escolhas externas."""
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

    class DummyResp:
        def json(self):
            return {"1001": 3, "1002": 1}

    with patch(
        "cargos.services.cargos_service.EscolhasAPIService.get_escolhas_por_cargo",
        return_value=DummyResp(),
    ):
        dados = CargosService.listar_autorizacoes_publicadas_agregadas()

    by_codigo = {item["codigo"]: item for item in dados}
    assert by_codigo[1001]["autorizacoes"] == 3
    assert by_codigo[1001]["total_escolhas"] == 3
    assert by_codigo[1001]["data_autorizacao_mais_recente"] == "2026-01-15"
    assert by_codigo[1002]["autorizacoes"] == 5
    assert by_codigo[1002]["total_escolhas"] == 1


# --- CargoRepository ---


def test_repositorio_obter_por_uuid_retorna_serializado(cargo_analista):
    """obter_por_uuid devolve dict com uuid/nome."""
    data = CargoRepository.obter_por_uuid(cargo_analista.uuid)
    assert data is not None
    assert data["uuid"] == str(cargo_analista.uuid)
    assert data["nome"] == "Analista de Sistemas"


def test_repositorio_obter_por_uuid_inexistente():
    """UUID desconhecido retorna None."""
    assert CargoRepository.obter_por_uuid(uuid4()) is None


def test_repositorio_listar_com_resumo_autorizacoes():
    """listar_com_resumo_autorizacoes soma autorizações por cargo."""
    cargo = Cargo.objects.create(nome="Cargo X", codigo=50)
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=4, data_autorizacao=date(2026, 2, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=6, data_autorizacao=date(2026, 3, 1)
    )
    resumo = CargoRepository.listar_com_resumo_autorizacoes()
    item = next(i for i in resumo if i["codigo"] == 50)
    assert item["autorizacoes"] == 10
    assert item["data_autorizacao_mais_recente"] == "2026-03-01"
