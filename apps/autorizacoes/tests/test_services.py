"""Testes unitários dos services e repository de autorizações."""

from datetime import date

import pytest

from autorizacoes.models import AutorizacaoPublicada
from autorizacoes.repository import AuthorizationRepository
from autorizacoes.services import montar_extracao_dados
from cargos.models import Cargo
from concursos.models import Concurso

pytestmark = pytest.mark.django_db


def test_montar_extracao_dados_total_sem_filtro():
    """Sem filtros, soma todas as autorizações com data."""
    cargo = Cargo.objects.create(nome="Cargo A", codigo=1)
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=10, data_autorizacao=date(2026, 1, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=5, data_autorizacao=None
    )
    resultado = montar_extracao_dados()
    assert resultado["autorizacoes-publicadas"] == 10
    assert len(resultado["cargos"]) == 1
    assert resultado["cargos"][0]["autorizacoes"] == 10


def test_montar_extracao_dados_filtra_por_concurso_e_anos():
    """Restringe por cargos do concurso e anos informados."""
    cargo = Cargo.objects.create(nome="Cargo A", codigo=1)
    concurso = Concurso.objects.create(nome="C1")
    concurso.cargos.add(cargo)
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=100, data_autorizacao=date(2026, 3, 1)
    )
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=80, data_autorizacao=date(2025, 1, 5)
    )
    resultado = montar_extracao_dados(
        concurso_uuid=concurso.uuid, anos=[2026]
    )
    assert resultado == {
        "2026": {
            "autorizacoes-publicadas": 100,
            "cargos": [
                {
                    "uuid": str(cargo.uuid),
                    "nome": "Cargo A",
                    "codigo": 1,
                    "autorizacoes": 100,
                    "data_autorizacao": "2026-03-01",
                }
            ],
        }
    }


def test_repositorio_montar_extracao_dados_delegado():
    """AuthorizationRepository.montar_extracao_dados espelha o service."""
    cargo = Cargo.objects.create(nome="X", codigo=2)
    AutorizacaoPublicada.objects.create(
        cargo=cargo, autorizacoes=7, data_autorizacao=date(2024, 1, 1)
    )
    via_repo = AuthorizationRepository.montar_extracao_dados()
    via_svc = montar_extracao_dados()
    assert via_repo == via_svc
