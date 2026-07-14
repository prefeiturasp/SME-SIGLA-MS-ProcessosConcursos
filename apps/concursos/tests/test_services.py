"""Testes unitários dos services e repository de concursos."""

from unittest.mock import Mock, patch

import pytest
import requests
from rest_framework.test import APIRequestFactory

from concursos.api.views import ConcursoViewSet
from concursos.models import Concurso
from concursos.repository import ConcursoRepository
from concursos.serializers import (
    ConcursoListSerializer,
    ConcursoSelectSerializer,
)
from concursos.services import ConcursosService
from concursos.services import sme_integration as svc

pytestmark = pytest.mark.django_db


def _set_settings(settings, url="http://api.local", token="secret"):
    """Configura URL/token da SME Integração."""
    settings.SMEINTEGRACAO_API_URL = url
    settings.SMEINTEGRACAO_API_TOKEN = token


# --- sme_integration ---


def test_buscar_cargos_sucesso(settings):
    """Busca e normaliza cargos da SME."""
    _set_settings(settings)
    payload = [
        {"codigoCargo": 101, "nomeCargo": "Professor A"},
        {"codigoCargo": 102, "nomeCargo": "Professor B"},
    ]
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None

    with patch("requests.get", return_value=mock_resp) as mock_get:
        result = svc.buscar_cargos_de_smeintegracao()

    mock_get.assert_called_once_with(
        "http://api.local/api/cargos",
        headers={"x-api-eol-key": "secret", "Accept": "application/json"},
        timeout=30,
    )
    assert result == [
        {"codigo": "101", "nome": "Professor A"},
        {"codigo": "102", "nome": "Professor B"},
    ]


def test_buscar_cargos_payload_invalido(settings):
    """Payload fora de lista gera ValueError."""
    _set_settings(settings)
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = {"unexpected": "obj"}
    mock_resp.raise_for_status.return_value = None
    with (
        patch("requests.get", return_value=mock_resp),
        pytest.raises(ValueError),
    ):
        svc.buscar_cargos_de_smeintegracao()


def test_buscar_cargos_http_error(settings):
    """HTTPError é propagado."""
    _set_settings(settings)
    mock_resp = Mock()
    mock_resp.raise_for_status.side_effect = requests.HTTPError("boom")
    with (
        patch("requests.get", return_value=mock_resp),
        pytest.raises(requests.HTTPError),
    ):
        svc.buscar_cargos_de_smeintegracao()


def test_buscar_concursos_sucesso(settings):
    """Busca e normaliza concursos da SME."""
    _set_settings(settings)
    payload = [
        {
            "codigo": 1,
            "descricao": "Concurso 2026",
            "numeroProcesso": 999,
            "cargos": [101, 102],
        }
    ]
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = payload
    mock_resp.raise_for_status.return_value = None
    with patch("requests.get", return_value=mock_resp) as mock_get:
        result = svc.buscar_concursos_de_smeintegracao()
    mock_get.assert_called_once_with(
        "http://api.local/api/concurso/tipos",
        headers={"x-api-eol-key": "secret", "Accept": "application/json"},
        timeout=30,
    )
    assert result == [
        {
            "codigo": 1,
            "nome": "Concurso 2026",
            "numero_processo": "999",
            "cargos": [101, 102],
        }
    ]


def test_buscar_concursos_payload_invalido(settings):
    """Payload de concursos inválido gera ValueError."""
    _set_settings(settings)
    mock_resp = Mock(status_code=200)
    mock_resp.json.return_value = {"unexpected": "obj"}
    mock_resp.raise_for_status.return_value = None
    with (
        patch("requests.get", return_value=mock_resp),
        pytest.raises(ValueError),
    ):
        svc.buscar_concursos_de_smeintegracao()


def test_settings_faltando_url(settings):
    """Sem URL da SME Integração falha."""
    _set_settings(settings, url=None, token="x")
    with pytest.raises(ValueError):
        svc.buscar_cargos_de_smeintegracao()


def test_settings_faltando_token(settings):
    """Sem token da SME Integração falha."""
    _set_settings(settings, url="http://api", token=None)
    with pytest.raises(ValueError):
        svc.buscar_concursos_de_smeintegracao()


# --- ConcursosService ---


def test_obter_serializer_listagem_select():
    """formato=select usa ConcursoSelectSerializer."""
    from rest_framework.request import Request

    factory = APIRequestFactory()
    request = Request(factory.get("/api/v1/concursos/", {"formato": "select"}))
    view = ConcursoViewSet()
    view.request = request
    view.format_kwarg = None
    assert (
        ConcursosService.obter_serializer_listagem(view, request)
        is ConcursoSelectSerializer
    )


def test_obter_serializer_listagem_padrao():
    """Sem formato usa ConcursoListSerializer."""
    from rest_framework.request import Request

    factory = APIRequestFactory()
    request = Request(factory.get("/api/v1/concursos/"))
    view = ConcursoViewSet()
    view.request = request
    view.format_kwarg = None
    assert (
        ConcursosService.obter_serializer_listagem(view, request)
        is ConcursoListSerializer
    )


# --- ConcursoRepository ---


def test_repositorio_obter_por_uuid(concurso_analista):
    """obter_por_uuid devolve dict serializado."""
    data = ConcursoRepository.obter_por_uuid(concurso_analista.uuid)
    assert data is not None
    assert data["nome"] == "Concurso de Analista"


def test_repositorio_listar_uuids_cargos_vinculados(
    concurso_analista, cargo_analista
):
    """Lista UUIDs dos cargos do concurso."""
    uuids = ConcursoRepository.listar_uuids_cargos_vinculados(
        concurso_analista.uuid
    )
    assert cargo_analista.uuid in uuids


def test_repositorio_obter_modelo_por_uuid(concurso_analista):
    """obter_modelo_por_uuid retorna a instância."""
    assert (
        ConcursoRepository.obter_modelo_por_uuid(concurso_analista.uuid)
        == concurso_analista
    )
